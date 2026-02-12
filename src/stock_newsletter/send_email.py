import os
from datetime import datetime, time
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from .finance import StockData
from .html_content import HTML_Content
from . import config

# EMAIL_ADDRESS = 'seb.terrade99@gmail.com'
# EMAIL_PASSWORD = os.getenv('GMAIL_PYTHON_PASS')

date_today = datetime.today().strftime("%B %d, %Y")

image_cid = make_msgid(domain="gmail.com")

def wait_for_image(image_path, retries=10, delay=1):
    for _ in range(retries):
        if image_path.exists():
            return True
        time.sleep(delay)
    return False

def send_stock_email(recipients, tickers):
    msg = EmailMessage()
    msg['Subject'] = f"{date_today} Stock Report"
    msg['From'] = config.EMAIL_ADDRESS
    msg['To'] = recipients
    
    # Generate HTML content
    etf_table = HTML_Content.generate_etf_html()
    sector_table = HTML_Content.generate_sector_html()
    news_html = HTML_Content.generate_news_html()
    earnings_html = HTML_Content.generate_earnings_html()

    stock_cards = []
    image_attachments = []
    for ticker in tickers:
        try:
            data = StockData.fetchStockInfo(ticker)
            image_path = config.IMAGES_DIR / f"{ticker}_prediction.png"
            image_cid = make_msgid(domain="gmail.com")
            
            # Store for later attachment
            image_attachments.append((image_path, image_cid))
            
            # Generate HTML with image placeholder
            stock_cards.append(HTML_Content.generate_stock_card(ticker, data, image_cid))
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            stock_cards.append(f"""
            <div style="color: #ef4444; padding: 10px;">
                Error loading data for {ticker}
            </div>
            """)

    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head></head>
    <body>
        <div class="email-container">
            <div class="header" style="text-align: center;">
                <h1>Stock Daily - {date_today}</h1>
            </div>
            <table class="stock-card" width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td style="padding: 10px; background: #ffffff; border-radius: 5px;">

                            <!-- ETF Grid -->
                            <div style="margin-bottom: 40px;">
                                {''.join(etf_table)}
                            </div>

                            <!-- Sector Grid -->
                            <div style="margin-bottom: 40px;">
                                {''.join(sector_table)}
                            </div>

                            <!-- Earnings Grid -->
                            <div>
                                {earnings_html}
                            </div>

                            <!-- News Grid -->
                            <div>
                                {news_html}
                            </div>
                        </td>
                    </tr>
                </table>
            {''.join(stock_cards)}
        </div>
    </body>
    </html>
    """
    
    msg.set_content(html_content, subtype='html')


    #Send Email
    for image_path, image_cid in image_attachments:
            try:
                if wait_for_image(image_path):
                    with open(image_path, "rb") as img_file:
                        msg.add_attachment(
                            img_file.read(),
                            maintype="image",
                            subtype="png",
                            cid=image_cid
                        )
                else:
                    print(f"⚠️ Warning: Image file '{image_path}' not found!")
            except Exception as e:
                print(f"Error attaching image {image_path}: {str(e)}")

    if not config.EMAIL_PASSWORD:
         print("No email password found. Skipping email send.")
         return

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            
            smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            smtp.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
         print(f"Failed to send email: {e}")