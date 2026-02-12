import sys
from pathlib import Path
from sqlmodel import select, Session

# Add src to python path to allow imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from stock_newsletter import send_email, config, database
from stock_newsletter.models import User

def main():
    print("Starting Stock Newsletter...")
    
    # Initialize Database
    database.create_db_and_tables()
    
    # Check for API keys
    if not config.API_KEY_TIINGO:
        print("Error: API_KEY_TIINGO not found in environment variables.")
        return

    # Create a default user if none exists (for testing/first run)
    with Session(database.engine) as session:
        default_user_email = config.EMAIL_ADDRESS
        user = session.exec(select(User).where(User.email == default_user_email)).first()
        if not user:
            print(f"Creating default user {default_user_email} with default tickers...")
            user = database.create_user(session, default_user_email)
            database.add_user_preference(session, user, "NVDA")
            database.add_user_preference(session, user, "TSLA")
        
        # Get all users and their preferences
        users = session.exec(select(User).where(User.is_active == True)).all()
        
        for user in users:
            tickers = [pref.ticker for pref in user.preferences]
            if not tickers:
                print(f"User {user.email} has no watched tickers. Skipping.")
                continue
                
            print(f"Fetching data and sending email to {user.email} for tickers: {tickers}")
            try:
                send_email.send_stock_email(user.email, tickers)
            except Exception as e:
                print(f"An error occurred for {user.email}: {e}")

if __name__ == "__main__":
    main()
