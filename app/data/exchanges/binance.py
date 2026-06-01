import ccxt
import pandas as pd
from .base import ExchangeConnector
from typing import Dict
from app.config import settings

class BinanceConnector(ExchangeConnector):
    def __init__(self, is_futures: bool = False):
        params = {
            "enableRateLimit": True,
            "apiKey": settings.BINANCE_API_KEY,
            "secret": settings.BINANCE_SECRET_KEY,
        }
        self.exchange = ccxt.binanceusdm(params) if is_futures else ccxt.binance(params)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
        return df

    def fetch_tickers(self) -> Dict:
        return self.exchange.fetch_tickers()
