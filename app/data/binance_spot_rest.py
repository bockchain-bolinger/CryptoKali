import requests
from typing import Optional

BASE = "https://api.binance.com"

def _get(path: str, params: Optional[dict] = None, timeout: int = 10):
    url = f"{BASE}{path}"
    r = requests.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def depth(symbol: str, limit: int = 100):
    return _get("/api/v3/depth", {"symbol": symbol, "limit": limit})
