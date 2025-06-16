import os
from datetime import datetime, time
import smtplib
from finance import StockData
from youtube import Youtube
from pandas.tseries.offsets import BDay
import pandas as pd

date_today = datetime.today().strftime("%B %d, %Y")

class HTML_Content:

    #Generate HTML for individual stock cards
    @staticmethod
    def generate_stock_card(ticker, data, image_cid):

        if data.loc['Yesterday','change_price']  > 0:
            symbol = "↑ +"
        else:
            symbol = "↓ -"



        return f"""
        <table class="stock-card" width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
                <td style="padding: 25px; background: #ffffff; border-radius: 12px;">
                    
                    <!-- Header -->
                    <table width="100%" border="0" cellspacing="0" cellpadding="0">
                        <tr>
                            <td style="padding-bottom: 15px; border-bottom: 1px solid #e2e8f0;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 22px; font-weight: 700; color: #1e293b;">
                                            {ticker} ${data.loc['Today','adjClose']:.2f} 
                                            <span style="color: {'#10b981' if data.loc['Yesterday','change_price'] > 0 else '#ef4444'}; font-weight: 600;">
                                                {symbol}{abs(data.loc['Yesterday','change_price']):.2f} ({data.loc['Yesterday','change_prc']:+.2f}%)
                                            </span>
                                        </td>
                                        <td align="right" style="color: #64748b; font-size: 14px;">
                                            Today • {date_today}
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>

                    <!-- Metrics Grid -->
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin: 20px 0;">
                        <tr>
                            <!-- Row 1 -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">Previous Close</div>
                                <div style="font-weight: 600; font-size: 15px;">${data.loc['Yesterday','adjClose']:.2f}</div>
                            </td>
                            <td width="2%"></td> <!-- Spacer column -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">Open</div>
                                <div style="font-weight: 600; font-size: 15px;">${data.loc['Today','open']:.2f}</div>
                            </td>
                            <td width="2%"></td> <!-- Spacer column -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">High</div>
                                <div style="font-weight: 600; font-size: 15px;">${data.loc['Today','high']:.2f}</div>
                            </td>
                            <td width="2%"></td> <!-- Spacer column -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">Low</div>
                                <div style="font-weight: 600; font-size: 15px;">${data.loc['Today','low']:.2f}</div>
                            </td>
                        </tr>

                        <!-- Spacer Row (8px height) -->
                        <tr height="8">
                            <td colspan="7" style="line-height: 8px; font-size: 8px;">&nbsp;</td>
                        </tr>

                        <tr>
                            <!-- Row 2 -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">Volume</div>
                                <div style="font-weight: 600; font-size: 15px;">{data.loc['Today','volume']/1e6:.1f}M</div>
                            </td>
                            <td width="2%"></td> <!-- Spacer column -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">Week %</div>
                                <div style="font-weight: 600; font-size: 15px; color: {'#10b981' if data.loc['Last Week','change_price'] > 0 else '#ef4444'}">
                                    {data.loc['Last Week','change_prc']:+.1f}%
                                </div>
                            </td>
                            <td width="2%"></td> <!-- Spacer column -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">Month %</div>
                                <div style="font-weight: 600; font-size: 15px; color: {'#10b981' if data.loc['Last Month','change_price'] > 0 else '#ef4444'}">
                                    {data.loc['Last Month','change_prc']:+.1f}%
                                </div>
                            </td>
                            <td width="2%"></td> <!-- Spacer column -->
                            <td width="23%" style="padding: 12px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 13px; color: #64748b;">YTD %</div>
                                <div style="font-weight: 600; font-size: 15px; color: {'#10b981' if data.loc['YTD','change_price'] > 0 else '#ef4444'}">
                                    {data.loc['YTD','change_prc']:+.1f}%
                                </div>
                            </td>
                        </tr>
                    </table>

                    <!-- Graph -->
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-top: 25px;">
                        <tr>
                            <td>
                                <h3 style="margin: 0 0 15px 0; font-family: 'Segoe UI', Arial, sans-serif;">Last 100 day Data</h3>
                                <div style="height: 250px; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                    <img src="cid:{image_cid[1:-1]}" alt="{ticker} chart" width="100%" style="max-height: 100%; object-fit: contain;">
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """
    
    #Generate ETF summary HTML
    @staticmethod
    def generate_etf_html():

        etfs = ['SPY', 'QQQ', 'DIA', 'IWM', 'SMH']

        etfs_df = []

        for etf in etfs:
            etf_data = StockData.fetchETFInfo(etf)
            etfs_df.append([etf] + list(etf_data))

        html = """
        <div style="text-align: center;">
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; margin: auto;">
                <thead>
                    <tr>
                        <th>ETF</th>
                        <th>Close</th>
                        <th>Prev Close</th>
                        <th>Change</th>
                        <th>% Change</th>
                        <th>% WEEK</th>
                        <th>% MONTH</th>
                        <th>% YTD</th>
                    </tr>
                </thead>
                <tbody>
        """

        for data in etfs_df:
            def color(val):
                if val > 0:
                    return 'green'
                elif val < 0:
                    return 'red'

            html += f"""
                <tr>
                    <td style = "color:#21618c"><b>{data[0]}</b></td>
                    <td><b>${data[1]:.2f}</b></td>
                    <td><b>${data[2]:.2f}</b></td>
                    <td style = "color:{color(data[3])}"><b>{data[3]:.2f}</b></td>
                    <td style = "color:{color(data[4])}"><b>{data[4]:.2f}%</b></td>
                    <td style = "color:{color(data[5])}"><b>{data[5]:.2f}%</b></td>
                    <td style = "color:{color(data[6])}"><b>{data[6]:.2f}%</b></td>
                    <td style = "color:{color(data[7])}"><b>{data[7]:.2f}%</b></td>

                </tr>
            """

        html += """
                </tbody>
            </table>
        </div>
        """

        return html
    
    #Generate Sector Info Summary HTML
    @staticmethod
    def generate_sector_html():

        etfs = [['XLK', 'Technology'], ['XLE', 'Energy'], ['XLF', 'Financials'], ['XLC', 'Communication Services'], ['XLY', 'Consumer Discretionary'], ['XLP', 'Consumer Staples'], 
                ['XLV', 'Health Care'], ['XLI', 'Industrials'], ['XLU', 'Utilities'], ['XLB', 'Materials'], ['XLRE', 'Real Estate']]

        etfs_df = []

        for etf in etfs:
            etf_data = StockData.fetchETFInfo(etf[0])
            etfs_df.append([etf[1]] + list(etf_data))

        html = """
        <div style="text-align: center;">
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; margin: auto;">
                <thead>
                    <tr>
                        <th>Sector</th>
                        <th>Close</th>
                        <th>Prev Close</th>
                        <th>Change</th>
                        <th>% Change</th>
                        <th>% WEEK</th>
                        <th>% MONTH</th>
                        <th>% YTD</th>
                    </tr>
                </thead>
                <tbody>
        """

        for data in etfs_df:
            print(data)
            def color(val):
                if val > 0:
                    return 'green'
                elif val < 0:
                    return 'red'

            html += f"""
                        <tr>
                            <td style = "color:#21618c"><b>{data[0]}</b></td>
                            <td><b>${data[1]:.2f}</b></td>
                            <td><b>${data[2]:.2f}</b></td>
                            <td style = "color:{color(data[3])}"><b>{data[3]:.2f}</b></td>
                            <td style = "color:{color(data[4])}"><b>{data[4]:.2f}%</b></td>
                            <td style = "color:{color(data[5])}"><b>{data[5]:.2f}%</b></td>
                            <td style = "color:{color(data[6])}"><b>{data[6]:.2f}%</b></td>
                            <td style = "color:{color(data[7])}"><b>{data[7]:.2f}%</b></td>

                        </tr>
                    """

        html += """
                </tbody>
            </table>
            <div>
                <p>See additional sector ETF info 
                    <a href="https://www.sectorspdrs.com/sectortracker" style="color:#0066cc; text-decoration:none" target="_blank">here</a>.
                </p>
            </div>
        </div>
        """

        return html
    
    #Generate News HTML
    @staticmethod
    def generate_news_html():
        news_info = StockData.fetchNews()
        youtube_channels = ['@alphatrends', '@GrahamStephan', '@Trade-IdeasPromotional', '@TomNashTV']

        html_content = """
        <div style="font-family:Arial,sans-serif; margin:0; background: white; display:flex; gap:15px;">
            <!-- News Column -->
            <div style="flex:1; background:white; padding:15px; border-radius:5px; box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <h2 style="margin:0 0 15px 0; padding-bottom:10px; border-bottom:1px solid #eee; text-align:center">Top Market News</h2>
        """
        
        for news in news_info:
            html_content += f"""
                <div style="margin-bottom:10px; padding:10px; border:1px solid #ddd; border-radius:4px">
                        <div style="font-weight:bold; margin-bottom:8px;">
                            <p>{news[1]}</p>
                            <a href="{news[0]}" style="color:#0066cc; text-decoration:none;" target="_blank">View article</a>
                        </div>
                    </div>
            """
        
        html_content += """
            </div>
            
            <!-- YouTube Column -->
            <div style="flex:1; background:white; padding:15px; border-radius:5px; box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <h2 style="margin:0 0 15px 0; padding-bottom:10px; border-bottom:1px solid #eee; text-align:center">Top Market Videos</h2>
        """
        
        for channel in youtube_channels:
            channel_id = Youtube.get_channel_id(channel)
            if channel_id:
                url, title = Youtube.get_latest_video(channel_id)
                html_content += f"""
                    <div style="margin-bottom:10px; padding:10px; border:1px solid #ddd; border-radius:4px">
                        <div style="font-weight:bold; margin-bottom:8px;">
                            <p>{channel} - {title}</p>
                            <a href="{url}" style="color:#0066cc; text-decoration:none;" target="_blank">Watch video</a>
                        </div>
                    </div>
                """
        
        html_content += """
            </div>
        </div>
        """

        return html_content
    
    @staticmethod
    def generate_earnings_html():
        # Get earnings data from fetchEarnings()
        earnings_data = StockData.fetchEarnings()
        
        # Create HTML header with date info
        next_trading_day = (datetime.today() + BDay(1)).strftime("%B %d, %Y")
        html_content = f"""
        <div style="font-family:Arial,sans-serif; max-width:1200px; margin:0 auto; background:white; padding:20px;">
            <div style="background:white; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1)">
                <h2 style="margin:0 0 10px 0; color:#2c3e50; text-align:center;">
                    Upcoming Earnings - {next_trading_day}
                </h2>
                <p style="text-align:center; color:#7f8c8d; margin-bottom:20px;">
                    Showing companies with revenue > $10B | {len(earnings_data)} companies reporting
                </p>
                
                <div style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead>
                            <tr style="background-color:#3498db; color:white;">
                                <th style="padding:12px 8px; text-align:left;">Company</th>
                                <th style="padding:12px 8px; text-align:center;">EPS Estimate</th>
                                <th style="padding:12px 8px; text-align:center;">Report Time</th>
                                <th style="padding:12px 8px; text-align:right;">Revenue Estimate</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Add each earnings row to the table
        for _, row in earnings_data.iterrows():
            eps = row['epsEstimate']
            eps_color = "color:#27ae60;" if (isinstance(eps, (int, float)) and eps >= 0) else "color:#e74c3c;"
            eps_display = f"{eps:,.2f}" if pd.notna(eps) else "N/A"
            
            html_content += f"""
                            <tr style="border-bottom:1px solid #ecf0f1;">
                                <td style="padding:10px 8px; font-weight:bold;">{row['symbol']}</td>
                                <td style="padding:10px 8px; text-align:center; {eps_color}">{eps_display}</td>
                                <td style="padding:10px 8px; text-align:center;">{row['hour']}</td>
                                <td style="padding:10px 8px; text-align:right; font-weight:bold;">{row['display_revenue']}</td>
                            </tr>
            """
        
        # Close HTML tags
        html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        """
        
        return html_content