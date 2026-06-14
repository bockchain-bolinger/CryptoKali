import pandas as pd
from app.agents.strategies.base_strategy import BaseStrategy

class MomentumWhaleStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="Momentum Whale Scalper",
            description="Scalping-Strategie, die auf massives Whale-Volumen (CVD Spikes) reagiert."
        )

    def analyze(self, symbol: str, df: pd.DataFrame, context: dict) -> dict:
        whale_data = context.get("whale_data", {})
        cvd = whale_data.get("cvd", {}).get(symbol, 0)
        recent_whales = whale_data.get("recent_whales", [])
        
        # Check if there's a huge whale buy in the last few minutes for this symbol
        symbol_whales = [w for w in recent_whales if w["symbol"] == symbol]
        
        if not symbol_whales:
            return {"signal": "NO-GO", "side": "NEUTRAL", "confidence": 0.0, "reason": "Keine Wal-Aktivität"}

        latest_whale = symbol_whales[0]
        
        # If the latest whale was a massive BUY and overall CVD is positive
        if latest_whale["side"] == "BUY" and latest_whale["value_usdt"] > 100_000 and cvd > 50_000:
            return {
                "signal": "GO",
                "side": "LONG",
                "confidence": 0.9,
                "reason": f"Massenhafter Wal-Einkauf erkannt (${latest_whale['value_usdt']:,.0f}). Momentum ist stark bullisch."
            }
            
        # If the latest whale was a massive SELL and overall CVD is negative
        if latest_whale["side"] == "SELL" and latest_whale["value_usdt"] > 100_000 and cvd < -50_000:
            return {
                "signal": "GO",
                "side": "SHORT",
                "confidence": 0.9,
                "reason": f"Massiver Wal-Abverkauf erkannt (${latest_whale['value_usdt']:,.0f}). Momentum ist stark bärisch."
            }

        return {"signal": "NO-GO", "side": "NEUTRAL", "confidence": 0.4, "reason": "Wal-Aktivität nicht signifikant genug."}
