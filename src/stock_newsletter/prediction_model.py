import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM, Input

from . import config

class PredictionModels:

    @staticmethod
    def predict_stock_price(ticker, start_date, end_date):
        
        #Data Collection from Tiingo API
        url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&token={config.API_KEY_TIINGO}"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)

        if df.empty:
            print(f"No data found for {ticker}")
            return pd.DataFrame() # Return empty if no data

        df_close = df.reset_index()['adjClose'] #Target Column

        #Reshape Close columns data between 0-1 (LSTM models are sensitive to the scale of data)
        scaler = MinMaxScaler(feature_range=(0,1))
        df_close = scaler.fit_transform(np.array(df_close).reshape(-1,1)) #Convert into array with values 0-1

        #Split dataset into Train and Test
        training_size = int(len(df_close)*0.65)
        # testing_size = len(df_close)-training_size
        train_data, test_data = df_close[0:training_size,:], df_close[training_size:len(df_close),:1]

        def create_dataset(dataset, time_step=1):
            dataX, dataY = [], []
            for i in range(len(dataset)-time_step-1):
                a = dataset[i:(i+time_step),0]
                dataX.append(a)
                dataY.append(dataset[i + time_step,0])
            return np.array(dataX), np.array(dataY)
        
        time_step = 100
        Xtrain, Ytrain = create_dataset(train_data, time_step)
        Xtest, Ytest = create_dataset(test_data, time_step)

        if len(Xtrain) == 0 or len(Xtest) == 0:
             print(f"Not enough data to train model for {ticker}")
             return pd.DataFrame()

        #Create the Stacked LSTM Model
        Xtrain =Xtrain.reshape(Xtrain.shape[0],Xtrain.shape[1] , 1)
        Xtest = Xtest.reshape(Xtest.shape[0],Xtest.shape[1] , 1)

        model = Sequential([
            Input(shape=(100, 1)),  # Explicit Input Layer
            LSTM(50, return_sequences=True),
            LSTM(50, return_sequences=True),
            LSTM(50),
            Dense(1)
        ])
        model.compile(loss='mean_squared_error', optimizer='adam')

        model.fit(Xtrain,Ytrain,validation_data=(Xtest,Ytest),epochs=10,batch_size=64,verbose=0) # Reduced epochs for production speed, verbose=0

        # train_predict = model.predict(Xtrain)
        # test_predict = model.predict(Xtest)

        ##Transformback to original form
        # train_predict=scaler.inverse_transform(train_predict)
        # test_predict=scaler.inverse_transform(test_predict)

        # Ytrain_inv = scaler.inverse_transform(Ytrain.reshape(-1, 1))
        # Ytest_inv = scaler.inverse_transform(Ytest.reshape(-1, 1))

        ### Calculate RMSE performance metrics
        # import math
        # from sklearn.metrics import mean_squared_error

        # rmse_train = math.sqrt(mean_squared_error(Ytrain_inv, train_predict))
        # rmse_test = math.sqrt(mean_squared_error(Ytest_inv, test_predict))
        # mean_price_train = np.mean(Ytrain_inv)
        # mean_price_test = np.mean(Ytest_inv)
        # nrmse_train = (rmse_train / mean_price_train) * 100
        # nrmse_test = (rmse_test / mean_price_test) * 100

        x_input=test_data[len(test_data)-100:].reshape(1,-1)
        temp_input=list(x_input)
        temp_input=temp_input[0].tolist()

        # demonstrate prediction for next 10 days
        # from numpy import array

        lst_output=[]
        n_steps=100
        i=0
        while(i<30):
            
            if(len(temp_input)>100):
                #print(temp_input)
                x_input=np.array(temp_input[1:])
                #print("{} day input {}".format(i,x_input))
                x_input=x_input.reshape(1,-1)
                x_input = x_input.reshape((1, n_steps, 1))
                #print(x_input)
                yhat = model.predict(x_input, verbose=0)
                #print("{} day output {}".format(i,yhat))
                temp_input.extend(yhat[0].tolist())
                temp_input=temp_input[1:]
                #print(temp_input)
                lst_output.extend(yhat.tolist())
                i=i+1
            else:
                x_input = x_input.reshape((1, n_steps,1))
                yhat = model.predict(x_input, verbose=0)
                #print(yhat[0])
                temp_input.extend(yhat[0].tolist())
                #print(len(temp_input))
                lst_output.extend(yhat.tolist())
                i=i+1

        dates = pd.to_datetime(df['date'])
        last_100_days_dates = dates[-100:]
        predicted_dates = pd.date_range(last_100_days_dates.iloc[-1] + pd.Timedelta(days=1), periods=30, freq='D')
        
        # Plot the original data with dates
        plt.figure(figsize=(12,6))
        plt.plot(last_100_days_dates, scaler.inverse_transform(df_close[-100:]), label='Current Data')

        # Plot the predicted data with dates
        plt.plot(predicted_dates, scaler.inverse_transform(lst_output), label='Future Predicted Data')

        # Formatting the plot
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'{ticker} Price Prediction')
        plt.legend()

        # Customize date formatting and tick frequency
        ax = plt.gca()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))  # Format as YYYY-MM-DD
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=10))  # Show ticks every 10 days

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Adjust layout to make room for the rotated x-axis labels
        plt.tight_layout()

        image_path = config.IMAGES_DIR / f'{ticker}_prediction.png'
        plt.savefig(image_path, dpi=300, bbox_inches='tight')
        plt.close()

        #Get latest metrics
        data = []
        data.append(df[['date', 'adjClose', 'high', 'low', 'open', 'volume']].iloc[-1]) #today
        data.append(df[['date', 'adjClose', 'high', 'low', 'open', 'volume']].iloc[-2]) #yesterday
        data.append(df[['date', 'adjClose', 'high', 'low', 'open', 'volume']].iloc[-6]) #last week
        data.append(df[['date', 'adjClose', 'high', 'low', 'open', 'volume']].iloc[-22]) #last month

        current_year = pd.to_datetime(df['date'].iloc[-1]).year
        ytd = df[pd.to_datetime(df['date']).dt.year == current_year].iloc[0] if len(df[pd.to_datetime(df['date']).dt.year == current_year]) > 0 else None
        data.append(ytd[['date', 'adjClose', 'high', 'low', 'open', 'volume']] if ytd is not None else None) #YTD

        

        if len(df)>=253: 
            data.append(df[['date', 'adjClose', 'high', 'low', 'open', 'volume']].iloc[-253]) #last year

        periods = ['Today', 'Yesterday', 'Last Week', 'Last Month', 'YTD', 'Last Year']
        # If we have less than 6 rows, we need to handle it or just let it crash/warn. 
        # But assuming inputs are good for now.
        
        # We might have None in data if ytd is None
        # Let's just create DataFrame and filter
        
        data_df = pd.DataFrame(data, index=periods[:len(data)])
        
        current_close = data_df.loc['Today','adjClose']
        current_volume = data_df.loc['Today','volume']
        data_df['change_price'] = current_close - data_df['adjClose']
        data_df['change_prc'] = (data_df['change_price']/data_df['adjClose'])*100
        data_df['change_vol'] = ((current_volume - data_df['volume'])/data_df['volume'])*100

        # print(current_close)
        # print(data_df.loc['Yesterday', 'adjClose'])

        data_df = data_df[['date', 'adjClose', 'open', 'high', 'low', 'volume', 'change_price', 'change_prc', 'change_vol']]

        return data_df
