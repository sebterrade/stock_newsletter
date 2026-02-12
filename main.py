import sys
from pathlib import Path

# Add src to python path to allow imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from stock_newsletter import send_email, config

def main():
    print("Starting Stock Newsletter...")
    
    # Check for API keys
    if not config.API_KEY_TIINGO:
        print("Error: API_KEY_TIINGO not found in environment variables.")
        return

    tickers = ['NVDA', 'TSLA']
    recipients = config.EMAIL_ADDRESS
    
    print(f"Fetching data and sending email for tickers: {tickers}")
    try:
        send_email.send_stock_email(recipients, tickers)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
