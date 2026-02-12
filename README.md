# Stock Market Newsletter

A Python application that generates and emails a stock market newsletter with predictions, news, and earnings reports.

## Setup

1.  **Clone the repository.**
2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment Variables:**
    *   Copy `.env.example` to `.env`.
    *   Fill in your API keys in `.env`.
    ```bash
    cp .env.example .env
    ```

## Usage

Run the main script:
```bash
python main.py
```

## features

*   **Stock Predictions**: Uses LSTM models to predict future stock prices.
*   **News Aggregation**: Scrapes CNBC for trending market news.
*   **YouTube Integration**: Fetches latest videos from financial channels.
*   **Earnings Reports**: Lists upcoming earnings for major companies.
*   **Email Reports**: Sends a formatted HTML email with all the above information.

## Project Structure

*   `src/stock_newsletter`: Source code.
*   `notebooks`: Jupyter notebooks for model development.
*   `data`: Generated data and logs.
