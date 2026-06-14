"""
sentiment_agent.py – Fetches Fear & Greed Index + CryptoPanic news sentiment.
"""
from app.agents.base_agent import BaseAgent
import requests, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class SentimentAgent(BaseAgent):
    @property
    def name(self): return "SentimentAgent"
    
    @property  
    def description(self): return "Fetches Fear & Greed Index and news sentiment for crypto markets"
    
    def analyze(self, context: dict) -> dict:
        symbol = context.get("symbol", "BTC")
        
        # Fear & Greed
        fg = self._get_fear_greed()
        
        # News sentiment
        news = self._get_news(symbol)
        news_sentiment = self._calc_news_sentiment(news)
        
        # Overall sentiment score -1.0 to +1.0
        fg_normalized = (fg.get("value", 50) - 50) / 50  # -1 to +1
        overall = round((fg_normalized * 0.4 + news_sentiment * 0.6), 3)
        
        return {
            "agent": self.name,
            "symbol": symbol,
            "fear_greed_index": fg.get("value", 50),
            "fear_greed_label": fg.get("value_classification", "Neutral"),
            "news_sentiment": round(news_sentiment, 3),
            "overall_sentiment": overall,
            "news_items": news[:5],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _get_fear_greed(self) -> dict:
        try:
            r = requests.get("https://api.alternative.me/fng/", timeout=5)
            data = r.json()["data"][0]
            return {"value": int(data["value"]), "value_classification": data["value_classification"]}
        except Exception as e:
            logger.warning("Fear&Greed API failed: %s", e)
            return {"value": 50, "value_classification": "Neutral"}
    
    def _get_news(self, symbol: str) -> list:
        # Extract base currency (BTC from BTC/USDT)
        base = symbol.split("/")[0] if "/" in symbol else symbol
        try:
            url = f"https://cryptopanic.com/api/v1/posts/?auth_token=public&currencies={base}&filter=hot&public=true"
            r = requests.get(url, timeout=8)
            items = r.json().get("results", [])
            result = []
            for item in items[:10]:
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
    
    def _calc_news_sentiment(self, news_items: list) -> float:
        if not news_items:
            return 0.0
        # Simple keyword-based sentiment
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
