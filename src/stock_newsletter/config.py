import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "stock_newsletter.db"

# Ensure directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
API_KEY_FMP = os.getenv("API_KEY_FMP")
API_KEY_TIINGO = os.getenv("API_KEY_TIINGO")
API_KEY_AP = os.getenv("API_KEY_AP")
API_KEY_FINNHUB = os.getenv("API_KEY_FINNHUB")
API_KEY_YOUTUBE = os.getenv("API_KEY_YOUTUBE")
EMAIL_PASSWORD = os.getenv("GMAIL_PYTHON_PASS")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "seb.terrade99@gmail.com")

if not all([API_KEY_FMP, API_KEY_TIINGO, API_KEY_AP, API_KEY_FINNHUB, API_KEY_YOUTUBE, EMAIL_PASSWORD]):
    print("Warning: Some API keys or passwords are missing in environment variables.")
