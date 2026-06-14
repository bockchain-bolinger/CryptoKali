import pandas as pd
from app.agents.strategies.base_strategy import BaseStrategy

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="Trend Following (Swing)",
            description="Sichere Swing-Trading Strategie basierend auf gleitenden Durchschnitten und Marktstruktur."
        )

    def analyze(self, symbol: str, df: pd.DataFrame, context: dict) -> dict:
        bias = context.get("market_bias", "neutral")
        confidence = context.get("market_confidence", 0.0)
        
        if bias == "bullish" and confidence > 0.7:
            return {
                "signal": "GO",
                "side": "LONG",
                "confidence": confidence,
                "reason": "Starker Aufwärtstrend erkannt (EMA/MACD Alignment)."
            }
        elif bias == "bearish" and confidence > 0.7:
            return {
                "signal": "GO",
                "side": "SHORT",
                "confidence": confidence,
                "reason": "Starker Abwärtstrend erkannt (EMA/MACD Alignment)."
            }
            
        return {
            "signal": "NO-GO", 
            "side": "NEUTRAL", 
            "confidence": confidence, 
            "reason": "Kein klarer Trend oder mangelnde Konfidenz."
        }
