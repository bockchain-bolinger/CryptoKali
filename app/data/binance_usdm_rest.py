import requests
from typing import Optional

BASE = "https://fapi.binance.com"

def _get(path: str, params: Optional[dict] = None, timeout: int = 10):
    url = f"{BASE}{path}"
    r = requests.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def funding_rate_history(symbol: str, limit: int = 50):
    return _get("/fapi/v1/fundingRate", {"symbol": symbol, "limit": limit})

def open_interest(symbol: str):
    return _get("/fapi/v1/openInterest", {"symbol": symbol})

def all_force_orders(symbol: Optional[str] = None, limit: int = 100, startTime: Optional[int] = None):
    params = {"limit": limit}
    if symbol:
        params["symbol"] = symbol
    if startTime:
        params["startTime"] = startTime
    return _get("/fapi/v1/allForceOrders", params)

def depth(symbol: str, limit: int = 100):
    return _get("/fapi/v1/depth", {"symbol": symbol, "limit": limit})
