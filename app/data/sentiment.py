"""
sentiment.py - Legacy/standalone functions for sentiment fetching.
"""
import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def get_fear_greed_index() -> dict:
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=5)
        data = r.json()["data"][0]
        return {
            "value": int(data["value"]),
            "value_classification": data["value_classification"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.warning("Fear&Greed API failed: %s", e)
        return {
            "value": 50, 
            "value_classification": "Neutral",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def get_crypto_news(symbols=None, filter='hot') -> list:
    base = symbols.split("/")[0] if symbols and "/" in symbols else symbols
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token=public&filter={filter}&public=true"
    if base:
        url += f"&currencies={base}"
        
    try:
        r = requests.get(url, timeout=8)
        items = r.json().get("results", [])
        result = []
        for item in items[:20]:
            result.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "source": item.get("source", {}).get("title", ""),
                "published_at": item.get("published_at", ""),
                "currencies": [c["code"] for c in item.get("currencies", [])]
            })
        return result
    except Exception as e:
        logger.warning("CryptoPanic API failed: %s", e)
        return []

def calculate_news_sentiment(news_items) -> float:
    if not news_items:
        return 0.0
    positive_words = ["bull", "surge", "rally", "pump", "breakout", "gain", "high", "adoption", "buy", "up", "bullish", "rise", "soar", "ath"]
    negative_words = ["bear", "crash", "dump", "fall", "hack", "ban", "sell", "low", "bearish", "down", "drop", "loss", "fail", "scam", "liquidation"]
    total = 0
    for item in news_items:
        text = item.get("title", "").lower()
        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)
        total += (pos - neg)
    max_possible = len(news_items) * 3
    return max(-1.0, min(1.0, total / max_possible if max_possible > 0 else 0.0))
