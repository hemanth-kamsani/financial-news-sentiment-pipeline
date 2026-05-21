import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "JPM",
    "BAC", "GS", "MS", "BLK", "SCHW"
]


def fetch_news(ticker: str) -> list[dict]:
    """
    Fetch latest news headlines for a given ticker
    from Alpha Vantage News Sentiment API.
    """
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "limit": 10,
        "apikey": API_KEY,
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("feed", []):
        articles.append({
            "ticker": ticker,
            "title": item.get("title"),
            "summary": item.get("summary"),
            "source": item.get("source"),
            "published_at": item.get("time_published"),
            "url": item.get("url"),
            "fetched_at": datetime.utcnow().isoformat(),
        })

    return articles


def save_raw(articles: list[dict], ticker: str) -> str:
    """
    Save raw articles to data/raw/ as a JSON file.
    Returns the file path.
    """
    os.makedirs("data/raw", exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filepath = f"data/raw/{ticker}_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(articles, f, indent=2)

    print(f"Saved {len(articles)} articles → {filepath}")
    return filepath


def run():
    """
    Main entry point. Loops over all tickers,
    fetches news, saves raw JSON.
    """
    all_articles = []

    for ticker in TICKERS:
        print(f"Fetching news for {ticker}...")
        try:
            articles = fetch_news(ticker)
            save_raw(articles, ticker)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    print(f"\nDone. Total articles fetched: {len(all_articles)}")
    return all_articles


if __name__ == "__main__":
    run()
