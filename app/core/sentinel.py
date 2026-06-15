import logging
from typing import Dict, Any, Tuple
from app.db import get_historical_win_rate, get_paper_trades

logger = logging.getLogger(__name__)

class ApexSentinel:
    """
    ApexSentinel acts as the central Risk & Portfolio Manager.
    It evaluates every trade before execution and monitors global exposure.
    """
    def __init__(self):
        # Configurable Hard Limits
        self.MAX_RISK_PER_TRADE_PCT = 0.02  # 2% max risk per trade
        self.MAX_OPEN_POSITIONS = 3
        self.MAX_DAILY_DRAWDOWN_PCT = 0.05  # 5% max daily drawdown (Circuit Breaker)
        self.CIRCUIT_BREAKER_ACTIVE = False
        
        # State
        self.total_capital = 10000.0 # Will be updated dynamically via DB/Exchange later
        
    def _check_circuit_breaker(self) -> Tuple[bool, str]:
        """Check if global risk limits are breached."""
        if self.CIRCUIT_BREAKER_ACTIVE:
            return False, "Circuit Breaker is active. Trading paused."
            
        # Simplified Daily Drawdown Check (Mocked for now, would pull actual daily PnL from DB)
        # In a real scenario, sum(pnl) of today's closed trades + unrealized pnl of open trades
        # If (total_pnl / capital) < -0.05 -> Activate
        
        return True, "Global risk checks passed."

    def _check_position_limits(self) -> Tuple[bool, str]:
        """Check if we have too many open positions."""
        try:
            open_trades = get_paper_trades(status='open')
            if len(open_trades) >= self.MAX_OPEN_POSITIONS:
                return False, f"Max open positions ({self.MAX_OPEN_POSITIONS}) reached."
        except Exception as e:
            logger.warning(f"Could not check open positions: {e}")
            
        return True, "Position limits passed."

    def evaluate_trade(self, symbol: str, direction: str, confidence: float, entry_price: float, stop_loss: float = None) -> Dict[str, Any]:
        """
        Evaluate a trade and return sizing and approval status.
        """
        # 1. Global Checks
        cb_passed, cb_reason = self._check_circuit_breaker()
        if not cb_passed:
            logger.warning(f"Sentinel blocked trade for {symbol}: {cb_reason}")
            return {"approved": False, "reason": cb_reason, "suggested_size": 0.0}

        # 2. Position Limits
        pos_passed, pos_reason = self._check_position_limits()
        if not pos_passed:
            logger.warning(f"Sentinel blocked trade for {symbol}: {pos_reason}")
            return {"approved": False, "reason": pos_reason, "suggested_size": 0.0}

        # 3. Position Sizing (Kelly Criterion)
        win_rate = get_historical_win_rate()
        win_rate = max(0.1, min(0.9, win_rate))  # Bound between 10% and 90%
        
        # Simple Kelly: W - ((1 - W) / R)
        # Assuming Risk/Reward (R) is ~1.5 average
        r_factor = 1.5
        kelly_pct = win_rate - ((1.0 - win_rate) / r_factor)
        
        # Half-Kelly for safety
        kelly_pct = max(0.0, kelly_pct * 0.5)
        
        # Bound by Max Risk Per Trade
        final_risk_pct = min(kelly_pct, self.MAX_RISK_PER_TRADE_PCT)
        
        if final_risk_pct <= 0:
            return {"approved": False, "reason": "Kelly criterion suggests 0 allocation.", "suggested_size": 0.0}
            
        # If stop loss is provided, calculate size based on distance to stop
        if stop_loss and entry_price > 0:
            risk_amount = self.total_capital * final_risk_pct
            price_risk_pct = abs(entry_price - stop_loss) / entry_price
            if price_risk_pct == 0:
                price_risk_pct = 0.01 # Fallback 1%
            suggested_size = risk_amount / (entry_price * price_risk_pct)
        else:
            # Fallback simple fractional sizing
            suggested_size = (self.total_capital * final_risk_pct) / entry_price

        logger.info(f"Sentinel approved trade for {symbol}. Size: {suggested_size} (Risk: {final_risk_pct*100:.2f}%)")
        return {
            "approved": True, 
            "reason": "Risk checks passed", 
            "suggested_size": suggested_size,
            "risk_pct": final_risk_pct
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns current Sentinel status for the Dashboard."""
        try:
            open_positions = len(get_paper_trades(status='open'))
        except:
            open_positions = 0
            
        status_data = {
            "circuit_breaker_active": self.CIRCUIT_BREAKER_ACTIVE,
            "max_risk_per_trade_pct": self.MAX_RISK_PER_TRADE_PCT * 100,
            "max_daily_drawdown_pct": self.MAX_DAILY_DRAWDOWN_PCT * 100,
            "max_open_positions": self.MAX_OPEN_POSITIONS,
            "current_open_positions": open_positions,
            "total_capital_tracked": self.total_capital,
            "status": "DANGER" if self.CIRCUIT_BREAKER_ACTIVE else ("WARNING" if open_positions >= self.MAX_OPEN_POSITIONS else "SAFE")
        }
        
        return status_data

    def get_optimal_allocation(self, symbols: list) -> Dict[str, Any]:
        """Calculates optimal portfolio allocation."""
        from app.core.portfolio_optimizer import portfolio_optimizer
        return portfolio_optimizer.optimize_portfolio(symbols, self.total_capital)

# Global Singleton Instance
sentinel = ApexSentinel()
