from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def analyze(self, symbol: str, df: pd.DataFrame, context: dict) -> dict:
        """
        Analysiert den Markt und gibt ein Signal zurück.
        Return Format:
        {
            "signal": "GO" | "NO-GO",
            "side": "LONG" | "SHORT" | "NEUTRAL",
            "confidence": 0.0 - 1.0,
            "reason": "String reason"
        }
        """
        pass
