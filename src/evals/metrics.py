import os
import json
from dotenv import load_dotenv
from src.ai.sentiment import analyze_headline

load_dotenv()


def load_ground_truth(path: str = "data/ground_truth.json") -> list[dict]:
    """
    Load manually labeled headlines.
    """
    with open(path, "r") as f:
        return json.load(f)


def run_evals(ground_truth: list[dict]) -> list[dict]:
    """
    Run each headline through the LLM pipeline
    and compare against expected labels.
    """
    results = []

    for i, item in enumerate(ground_truth):
        print(f"Evaluating {i+1}/{len(ground_truth)}: {item['ticker']}...")

        llm_output = analyze_headline(item["headline"], item["ticker"])

        sentiment_match = (
            llm_output.get("sentiment") == item["expected_sentiment"]
        )
        event_match = (
            llm_output.get("event_type") == item["expected_event_type"]
        )

        results.append({
            "headline": item["headline"],
            "ticker": item["ticker"],
            "expected_sentiment": item["expected_sentiment"],
            "llm_sentiment": llm_output.get("sentiment"),
            "sentiment_match": sentiment_match,
            "expected_event_type": item["expected_event_type"],
            "llm_event_type": llm_output.get("event_type"),
            "event_match": event_match,
            "score": llm_output.get("score"),
            "confidence": llm_output.get("confidence"),
            "reasoning": llm_output.get("reasoning"),
        })

    return results


def compute_metrics(results: list[dict]) -> dict:
    """
    Compute accuracy metrics across all eval results.
    """
    total = len(results)
    sentiment_correct = sum(1 for r in results if r["sentiment_match"])
    event_correct = sum(1 for r in results if r["event_match"])
    both_correct = sum(1 for r in results if r["sentiment_match"] and r["event_match"])

    metrics = {
        "total_headlines": total,
        "sentiment_accuracy": round(sentiment_correct / total, 2),
        "event_type_accuracy": round(event_correct / total, 2),
        "overall_accuracy": round(both_correct / total, 2),
    }

    return metrics


def print_report(results: list[dict], metrics: dict):
    """
    Print a readable eval report.
    """
    print("\n" + "="*60)
    print("EVAL REPORT — Financial News Sentiment Pipeline")
    print("="*60)

    for r in results:
        sentiment_icon = "✅" if r["sentiment_match"] else "❌"
        event_icon = "✅" if r["event_match"] else "❌"
        print(f"\n{r['ticker']} | {r['headline'][:55]}...")
        print(f"  Sentiment {sentiment_icon} expected={r['expected_sentiment']} got={r['llm_sentiment']}")
        print(f"  Event     {event_icon} expected={r['expected_event_type']} got={r['llm_event_type']}")
        print(f"  Score={r['score']} | Confidence={r['confidence']}")

    print("\n" + "="*60)
    print("METRICS SUMMARY")
    print("="*60)
    print(f"Total headlines evaluated : {metrics['total_headlines']}")
    print(f"Sentiment accuracy        : {metrics['sentiment_accuracy'] * 100:.0f}%")
    print(f"Event type accuracy       : {metrics['event_type_accuracy'] * 100:.0f}%")
    print(f"Overall accuracy          : {metrics['overall_accuracy'] * 100:.0f}%")
    print("="*60)


if __name__ == "__main__":
    ground_truth = load_ground_truth()
    results = run_evals(ground_truth)
    metrics = compute_metrics(results)
    print_report(results, metrics)
