import pandas as pd
from typing import Dict, List, Literal
from app.config import settings
from app.data.exchanges.binance import BinanceConnector

MarketType = Literal["spot", "usdm"]

def _get_connector(market_type: MarketType):
    return BinanceConnector(is_futures=(market_type == "usdm"))

def fetch_ohlcv(symbol: str, timeframe: str, limit: int, market_type: MarketType) -> pd.DataFrame:
    connector = _get_connector(market_type)
    return connector.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

def build_universe_spot() -> List[str]:
    connector = _get_connector("spot")
    tickers: Dict = connector.fetch_tickers()
    out = []
    for sym, t in tickers.items():
        if sym.endswith(f"/{settings.QUOTE}"):
            qv = t.get("quoteVolume") or 0.0
            try:
                if float(qv) >= settings.MIN_QUOTE_VOLUME_USD_SPOT:
                    out.append(sym)
            except:
                pass
    return sorted(out)

def build_universe_usdm() -> List[str]:
    connector = _get_connector("usdm")
    tickers: Dict = connector.fetch_tickers()
    out = []
    for sym, t in tickers.items():
        if sym.endswith(f"/{settings.QUOTE}"):
            qv = t.get("quoteVolume") or 0.0
            try:
                if float(qv) >= settings.MIN_QUOTE_VOLUME_USD_FUT:
                    out.append(sym)
            except:
                pass
    return sorted(out)

def spot_to_rest_symbol(spot_symbol: str) -> str:
    return spot_symbol.replace("/", "")

def futures_to_rest_symbol(fut_symbol: str) -> str:
    return fut_symbol.replace("/", "")

