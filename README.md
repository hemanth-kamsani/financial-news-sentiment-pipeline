# Financial News Sentiment → Risk Signal Pipeline

An end-to-end AI-powered data pipeline that ingests real-time financial news, enriches it with LLM-based sentiment analysis, and generates equity risk signals stored in Snowflake.

## Architecture
## Tech Stack

| Layer | Tools |
|---|---|
| Ingestion | Alpha Vantage API, Python, Airflow |
| AI Enrichment | OpenAI GPT-4, Prompt Engineering |
| Storage | Snowflake, Chromadb, AWS S3 |
| Transformation | dbt Core |
| Evaluation | Custom eval suite, LangSmith |
| Infrastructure | Python venv, GitHub Actions |

## Project Structure
## Setup

```bash
git clone https://github.com/YOUR_USERNAME/financial-news-sentiment-pipeline.git
cd financial-news-sentiment-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
```

## Pipeline Phases

- **Phase 1 — Ingestion:** Pull financial news headlines for S&P 500 tickers via Alpha Vantage
- **Phase 2 — AI Enrichment:** Extract sentiment score, ticker, and event type using OpenAI
- **Phase 3 — Storage:** Load enriched signals into Snowflake, embeddings into ChromaDB
- **Phase 4 — Evals:** Measure sentiment accuracy against 50 labeled headlines

## Results

| Metric | Value |
|---|---|
| Tickers covered | 10 S&P 500 equities |
| News articles processed | 500+ |
| Sentiment accuracy | TBD |
| Avg enrichment latency | TBD |

## Author

Hemanth Reddy Kamsani — [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
