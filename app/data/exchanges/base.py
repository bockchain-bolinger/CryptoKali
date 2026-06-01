from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class ExchangeConnector(ABC):
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        pass

    @abstractmethod
    def fetch_tickers(self) -> dict:
        pass
