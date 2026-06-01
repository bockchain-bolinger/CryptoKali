from typing import Dict
from app.config import settings

class OrderbookSimulator:
    def __init__(self):
        self.fees_bps = settings.FEES_BPS
        self.slippage_bps = settings.SLIPPAGE_BPS

    def simulate_fill(self, target_price: float, current_high: float, current_low: float) -> float:
        # Simple slippage model based on spread
        spread = (current_high - current_low) / current_price_approximation(current_high, current_low)
        slippage = spread * (self.slippage_bps / 10000.0)
        return target_price * (1 + slippage)

    def apply_costs(self, pnl: float, entry: float, exit_price: float, units: float) -> float:
        notional = ((entry + exit_price) / 2.0) * units
        fees = notional * (self.fees_bps / 10000.0) * 2.0
        return pnl - fees

def current_price_approximation(high: float, low: float) -> float:
    return (high + low) / 2.0
