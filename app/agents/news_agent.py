"""
news_agent.py - Polls CryptoPanic and Binance Announcements.
"""
from app.agents.base_agent import BaseAgent
import requests, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class NewsAgent(BaseAgent):
    @property
    def name(self): return "NewsAgent"
    
    @property
    def description(self): return "Polls crypto news and announcements"
    
    def analyze(self, context: dict) -> dict:
        symbol = context.get("symbol", "BTC")
        
        panic_news = self._get_cryptopanic_news(symbol)
        binance_news = self._get_binance_announcements()
        
        all_items = panic_news + binance_news
        
        return {
            "agent": self.name,
            "items": all_items,
            "total": len(all_items),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    def _get_cryptopanic_news(self, symbol: str) -> list:
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
                    "source": item.get("source", {}).get("title", "CryptoPanic"),
                    "published_at": item.get("published_at", ""),
                    "sentiment": self._calc_text_sentiment(item.get("title", "")),
                    "currencies": [c["code"] for c in item.get("currencies", [])]
                })
            return result
        except Exception as e:
            logger.warning("CryptoPanic API failed in NewsAgent: %s", e)
            return []

    def _get_binance_announcements(self) -> list:
        try:
            url = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageSize=20&pageNo=1"
            r = requests.get(url, timeout=8)
            data = r.json()
            catalogs = data.get("data", {}).get("catalogs", [])
            result = []
            if catalogs:
                articles = catalogs[0].get("articles", [])
                for a in articles[:10]:
                    dt = datetime.fromtimestamp(a.get("releaseDate", 0) / 1000, tz=timezone.utc)
                    result.append({
                        "title": a.get("title", ""),
                        "url": f"https://www.binance.com/en/support/announcement/{a.get('code', '')}",
                        "source": "Binance Announcements",
                        "published_at": dt.isoformat(),
                        "sentiment": self._calc_text_sentiment(a.get("title", "")),
                        "currencies": []
                    })
            return result
        except Exception as e:
            logger.warning("Binance Announcements API failed: %s", e)
            return []

    def _calc_text_sentiment(self, text: str) -> float:
        positive_words = ["bull", "surge", "rally", "pump", "breakout", "gain", "high", "adoption", "buy", "up", "bullish", "rise", "soar", "ath", "listing", "launch"]
        negative_words = ["bear", "crash", "dump", "fall", "hack", "ban", "sell", "low", "bearish", "down", "drop", "loss", "fail", "scam", "liquidation", "delisting"]
        text = text.lower()
        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)
        total = pos - neg
        return max(-1.0, min(1.0, total / 3.0))
