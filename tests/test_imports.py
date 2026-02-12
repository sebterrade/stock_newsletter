import sys
from pathlib import Path

# Add src to python path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

try:
    from stock_newsletter import config
    from stock_newsletter import finance
    from stock_newsletter import html_content
    from stock_newsletter import prediction_model
    from stock_newsletter import send_email
    from stock_newsletter import youtube
    print("Successfully imported all modules.")
except ImportError as e:
    print(f"Failed to import modules: {e}")
    sys.exit(1)
