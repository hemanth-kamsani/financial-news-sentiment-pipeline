import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a senior financial risk analyst at a top-tier asset management firm.

Your job is to analyze financial news headlines and assess their impact on stock prices.

For each headline, return a JSON object with exactly these fields:
{
    "ticker": "the stock ticker symbol this news is most about",
    "sentiment": "positive, negative, or neutral",
    "score": a float between -1.0 (most negative) and 1.0 (most positive),
    "event_type": "one of: earnings, macroeconomic, legal, merger_acquisition, leadership, market, other",
    "confidence": a float between 0.0 and 1.0 indicating your confidence,
    "reasoning": "one sentence explaining your score"
}

Rules:
- Return valid JSON only. No extra text, no markdown, no explanation outside the JSON.
- score must reflect real market impact, not just tone.
- If the headline mentions multiple tickers, pick the most affected one.
- Be precise. A 0.85 score means strong positive signal, not just mildly good news.
"""


def analyze_headline(headline: str, ticker: str) -> dict:
    """
    Send a single headline to OpenAI and get back
    a structured sentiment analysis.
    """
    user_prompt = f"""
    Ticker context: {ticker}
    Headline: {headline}
    
    Analyze this headline and return the JSON risk signal.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "ticker": ticker,
            "sentiment": "unknown",
            "score": 0.0,
            "event_type": "other",
            "confidence": 0.0,
            "reasoning": "Failed to parse LLM response",
            "raw_response": raw,
        }

    result["original_headline"] = headline
    return result


def analyze_batch(articles: list[dict]) -> list[dict]:
    """
    Loop over a list of raw articles from the ingestion phase
    and enrich each one with sentiment analysis.
    """
    enriched = []

    for i, article in enumerate(articles):
        print(f"Analyzing {i+1}/{len(articles)}: {article['ticker']}...")
        try:
            result = analyze_headline(article["title"], article["ticker"])
            result["source"] = article.get("source")
            result["published_at"] = article.get("published_at")
            result["url"] = article.get("url")
            enriched.append(result)
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone. Enriched {len(enriched)} articles.")
    return enriched


if __name__ == "__main__":
    test_headlines = [
        {"ticker": "JPM", "title": "JPMorgan warns of recession risk as Fed holds rates steady", "source": "Reuters", "published_at": "2024-01-01", "url": ""},
        {"ticker": "GS",  "title": "Goldman Sachs beats Q3 earnings estimates by 12%", "source": "Bloomberg", "published_at": "2024-01-01", "url": ""},
        {"ticker": "BAC", "title": "Bank of America CEO unexpectedly resigns", "source": "WSJ", "published_at": "2024-01-01", "url": ""},
    ]

    results = analyze_batch(test_headlines)

    for r in results:
        print(f"\n{r['ticker']} | {r['sentiment']} | score: {r['score']}")
        print(f"  Event: {r['event_type']} | Confidence: {r['confidence']}")
        print(f"  Reasoning: {r['reasoning']}")
