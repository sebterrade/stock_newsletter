import requests
import pandas as pd
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import time
from pytube import YouTube, Channel
import re
import os

from . import config
from .prediction_model import PredictionModels

class StockData:

    @staticmethod
    def fetchStockInfo(ticker):

        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")

        stock_data = PredictionModels.predict_stock_price(ticker, start_date, end_date)

        return stock_data
    
    @staticmethod
    def fetchETFInfo(ticker):

        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")

        url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&token={config.API_KEY_TIINGO}"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)

        # print(df['adjClose'].iloc[-1])
        # print(df['adjClose'].iloc[-6])
        # print(df['adjClose'].iloc[-22])

        today_close = df['adjClose'].iloc[-1]
        previous_close = df['adjClose'].iloc[-2]
        price_change = today_close - previous_close
        perc_change = (price_change/previous_close)*100

        wk_perc_change = ((today_close - df['adjClose'].iloc[-6])/df['adjClose'].iloc[-6])*100
        month_perc_change = ((today_close - df['adjClose'].iloc[-22])/df['adjClose'].iloc[-22])*100

        current_year = pd.to_datetime(df['date'].iloc[-1]).year
        ytd = df[pd.to_datetime(df['date']).dt.year == current_year].iloc[0]
        ytd_perc_change = ((today_close - ytd['adjClose'])/ytd['adjClose'])*100

        return today_close, previous_close, price_change, perc_change, wk_perc_change, month_perc_change, ytd_perc_change
    
    @staticmethod
    def fetchNews():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        page_scrape = requests.get('https://www.cnbc.com/markets/', headers=headers)
        soup = BeautifulSoup(page_scrape.text, "html.parser")
        
        trending_items = soup.find_all('div', class_='TrendingNowItem-linkWrap')
        
        news_info = []
        if not trending_items:
            print("No trending items found. Check class names or page structure.")
        else:
            for item in trending_items:
                link = item.find('a')['href']
                title = item.find('a', class_='TrendingNowItem-title').get_text(strip=True)
                # print(f"Title: {title}\nURL: {link}\n" + "-" * 50)

                news_info.append([link, title])
                 
        return news_info
    
    @staticmethod
    def fetchEarnings():

        next_trading_day = (datetime.today() + BDay(1)).strftime('%Y-%m-%d')

        #Get data
        url = f'https://finnhub.io/api/v1/calendar/earnings?from={next_trading_day}&to={next_trading_day}&token={config.API_KEY_FINNHUB}'
        response = requests.get(url)
        data = response.json()

        # Convert to DataFrame
        df = pd.DataFrame(data.get("earningsCalendar", []))
        if df.empty:
             print(f"No earnings data found for {next_trading_day}")
             return pd.DataFrame()
             
        next_day_earnings = df[df['date'] == next_trading_day]  # Extra filter for safety
        
        # Filter for revenue > 10B if likely valid, but be careful if no companies match
        next_day_earnings = next_day_earnings[next_day_earnings['revenueEstimate'] > 10_000_000_000]

        next_day_earnings['hour'] = next_day_earnings['hour'].replace({
            'amc': 'After Market Close',
            'bmo': 'Before Market Open'
        })

        # Format revenue
        def format_revenue(value):
            if pd.isna(value):
                return "N/A"
            if value >= 1e9:
                return f"${value/1e9:,.1f}B"
            elif value >= 1e6:
                return f"${value/1e6:,.0f}M"
            return f"${value:,.0f}"

        # Create display DataFrame (preserve original for sorting)
        display_df = next_day_earnings[['symbol', 'epsEstimate', 'hour']].copy()
        display_df['revenue'] = next_day_earnings['revenueEstimate'].apply(format_revenue)
        
        # Sort by original revenue values (not formatted strings)
        sorted_df = next_day_earnings.assign(
            display_revenue=display_df['revenue']  # Carry forward formatted values
        ).sort_values('revenueEstimate', ascending=False)

        # Final output
        print(f"\nNext Trading Day: {next_trading_day}")
        print(f"Companies Reporting: {len(sorted_df)}\n")
        # print(sorted_df[['symbol', 'epsEstimate', 'hour', 'display_revenue']]
        #     .rename(columns={'display_revenue': 'revenueEstimate'})
        #     .reset_index(drop=True))
        
        return sorted_df
