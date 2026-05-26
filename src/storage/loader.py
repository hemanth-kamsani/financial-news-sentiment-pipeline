import os
import json
import duckdb
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "data/finance.db"


def get_connection():
    """
    Connect to local DuckDB database.
    Creates the file if it doesn't exist.
    """
    return duckdb.connect(DB_PATH)


def create_table():
    """
    Create SENTIMENT_SIGNALS table if it doesn't exist.
    """
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS sentiment_signals (
            ticker            VARCHAR,
            sentiment         VARCHAR,
            score             DOUBLE,
            event_type        VARCHAR,
            confidence        DOUBLE,
            reasoning         VARCHAR,
            original_headline VARCHAR,
            source            VARCHAR,
            published_at      VARCHAR,
            url               VARCHAR,
            loaded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.close()
    print("Table ready.")


def load_enriched(enriched_articles: list[dict]):
    """
    Insert enriched sentiment records into DuckDB.
    """
    con = get_connection()

    for article in enriched_articles:
        con.execute("""
            INSERT INTO sentiment_signals (
                ticker, sentiment, score, event_type,
                confidence, reasoning, original_headline,
                source, published_at, url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            article.get("ticker"),
            article.get("sentiment"),
            article.get("score"),
            article.get("event_type"),
            article.get("confidence"),
            article.get("reasoning"),
            article.get("original_headline"),
            article.get("source"),
            article.get("published_at"),
            article.get("url"),
        ])

    con.close()
    print(f"Loaded {len(enriched_articles)} records into sentiment_signals.")


def query_signals():
    """
    Preview what's in the table.
    """
    con = get_connection()
    result = con.execute("""
        SELECT ticker, sentiment, score, event_type, confidence
        FROM sentiment_signals
        ORDER BY score ASC
        LIMIT 20
    """).fetchdf()
    con.close()
    return result


if __name__ == "__main__":
    create_table()

    test_data = [
        {
            "ticker": "JPM",
            "sentiment": "negative",
            "score": -0.6,
            "event_type": "macroeconomic",
            "confidence": 0.88,
            "reasoning": "Recession warning signals credit risk for banking sector",
            "original_headline": "JPMorgan warns of recession risk as Fed holds rates steady",
            "source": "Reuters",
            "published_at": "2024-01-01",
            "url": "",
        },
        {
            "ticker": "GS",
            "sentiment": "positive",
            "score": 0.85,
            "event_type": "earnings",
            "confidence": 0.95,
            "reasoning": "Beating earnings by 12% is a strong positive signal",
            "original_headline": "Goldman Sachs beats Q3 earnings estimates by 12%",
            "source": "Bloomberg",
            "published_at": "2024-01-01",
            "url": "",
        },
        {
            "ticker": "BAC",
            "sentiment": "negative",
            "score": -0.7,
            "event_type": "leadership",
            "confidence": 0.8,
            "reasoning": "Unexpected resignation creates uncertainty",
            "original_headline": "Bank of America CEO unexpectedly resigns",
            "source": "WSJ",
            "published_at": "2024-01-01",
            "url": "",
        },
    ]

    load_enriched(test_data)

    print("\nCurrent signals in DB:")
    print(query_signals())
