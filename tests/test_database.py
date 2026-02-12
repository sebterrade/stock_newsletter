import sys
from pathlib import Path
from sqlmodel import Session, select, create_engine
import os

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from stock_newsletter import database, config
from stock_newsletter.models import User, Stock, UserPreference

# Use a temporary database for testing
TEST_DB_PATH = Path("test_stock_newsletter.db")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

sqlite_url = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(sqlite_url)

# Override the engine in database module for testing (monkey patching somewhat)
database.engine = engine

def test_database():
    print("Creating tables...")
    database.create_db_and_tables()
    
    with Session(database.engine) as session:
        print("Creating user...")
        user = database.create_user(session, "test@example.com")
        assert user.id is not None
        assert user.email == "test@example.com"
        
        print("Adding preference...")
        database.add_user_preference(session, user, "AAPL")
        database.add_user_preference(session, user, "GOOGL")
        
        print("Verifying preferences...")
        tickers = database.get_user_tickers(session, "test@example.com")
        assert "AAPL" in tickers
        assert "GOOGL" in tickers
        assert len(tickers) == 2
        
        print("Verifying persistence...")
        # Check if stocks were created
        stocks = session.exec(select(Stock)).all()
        assert len(stocks) == 2
        
    print("Database test passed!")

if __name__ == "__main__":
    try:
        test_database()
    finally:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
