"""
risk_agent.py – RiskAgent for Apex AI.

Evaluates a proposed trade plan against:
  • Kelly Criterion (half-Kelly sizing for safety)
  • Maximum drawdown guard (portfolio heat)
  • Correlation to already-open positions
  • Per-trade risk-% cap from config

Returns a risk-adjusted score and an approval decision.
"""

import logging
import math
from typing import Any, Dict, List, Optional

from app.agents.base_agent import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Full Kelly fraction.

    f* = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
    Clamped to [0, 1].
    """
    if avg_win <= 0 or avg_loss <= 0:
        return 0.0
    loss_rate = 1.0 - win_rate
    kelly = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
    return max(0.0, min(1.0, kelly))


def _correlation_penalty(symbol: str, open_positions: List[Dict]) -> float:
    """
    Naïve correlation penalty.

    Counts how many open positions share the same base currency as the
    candidate symbol.  Each overlap subtracts 0.1 from score.
    """
    if not open_positions:
        return 0.0

    base = symbol.split("/")[0].upper() if "/" in symbol else symbol[:3].upper()
    overlaps = sum(
        1 for p in open_positions
        if p.get("symbol", "").upper().startswith(base)
    )
    return min(overlaps * 0.10, 0.50)


def _portfolio_heat(open_positions: List[Dict], equity: float) -> float:
    """
    Return the current portfolio heat as a fraction of equity.

    Heat = Σ(position notional × risk_pct_per_trade) / equity
    We approximate each position's at-risk amount as:
      risk$ = entry_price × size × RISK_PCT_PER_TRADE
    """
    if not open_positions or equity <= 0:
        return 0.0
    total_risk = sum(
        (p.get("entry_price", 0) or 0) * (p.get("size", 0) or 0) * settings.RISK_PCT_PER_TRADE
        for p in open_positions
    )
    return min(total_risk / equity, 1.0)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class RiskAgent(BaseAgent):
    """
    Evaluates the risk profile of a trade plan and returns an approval
    decision together with a risk-adjusted score and optional size override.
    """

    # Maximum allowed portfolio heat before new trades are blocked
    MAX_PORTFOLIO_HEAT: float = 0.06  # 6 % of equity
    # Maximum risk score that still qualifies for approval
    MAX_RISK_SCORE_APPROVE: float = 7.5

    @property
    def name(self) -> str:
        return "RiskAgent"

    @property
    def description(self) -> str:
        return (
            "Evaluates a trade plan using Kelly Criterion, portfolio heat, "
            "max drawdown guard, and open-position correlation."
        )

    # ── Entry point ──────────────────────────────────────────────────────────

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parameters
        ----------
        context : dict
            Required / optional keys:
              • ``symbol``          – e.g. "BTC/USDT"
              • ``entry``           – proposed entry price
              • ``stop``            – stop-loss price
              • ``tp1``             – first take-profit
              • ``score``           – raw strategy score (0-100)
              • ``open_positions``  – list of open position dicts from DB
              • ``equity``          – current account equity (USD)
              • ``win_rate``        – historical win rate (0-1), default 0.45
              • ``avg_rr``          – average reward/risk, default 1.5

        Returns
        -------
        dict with keys: approved, risk_score, max_size_override, reason, agent
        """
        symbol: str = context.get("symbol", "UNKNOWN")
        entry: Optional[float] = context.get("entry")
        stop: Optional[float] = context.get("stop")
        tp1: Optional[float] = context.get("tp1")
        strategy_score: float = float(context.get("score", 50))
        open_positions: List[Dict] = context.get("open_positions", [])
        equity: float = float(context.get("equity", settings.ACCOUNT_EQUITY))
        win_rate: float = float(context.get("win_rate", 0.45))
        avg_rr: float = float(context.get("avg_rr", 1.5))

        reasons: List[str] = []
        risk_score: float = 0.0  # 0 = safe, 10 = extremely risky

        # ── 1. Risk-per-trade ratio ──────────────────────────────────────────
        rr_ratio: Optional[float] = None
        if entry and stop and tp1 and stop != entry:
            risk_dist = abs(entry - stop)
            reward_dist = abs(tp1 - entry)
            rr_ratio = reward_dist / risk_dist if risk_dist > 0 else None

        if rr_ratio is not None:
            if rr_ratio < 1.0:
                risk_score += 3.0
                reasons.append(f"Poor R:R ratio ({rr_ratio:.2f} < 1.0)")
            elif rr_ratio < 1.5:
                risk_score += 1.0
                reasons.append(f"Acceptable R:R ({rr_ratio:.2f})")
        else:
            risk_score += 1.5
            reasons.append("Could not compute R:R (missing entry/stop/tp1)")

        # ── 2. Kelly Criterion sizing ────────────────────────────────────────
        avg_win = avg_rr
        avg_loss = 1.0
        kelly = _kelly_fraction(win_rate, avg_win, avg_loss)
        half_kelly = kelly * 0.5  # use half-Kelly for safety

        max_size_pct = min(half_kelly, settings.RISK_PCT_PER_TRADE * 2)
        max_size_override = round(equity * max_size_pct, 2)

        if kelly < 0.05:
            risk_score += 2.0
            reasons.append(f"Negative/near-zero Kelly fraction ({kelly:.3f})")

        # ── 3. Portfolio heat ────────────────────────────────────────────────
        heat = _portfolio_heat(open_positions, equity)
        if heat > self.MAX_PORTFOLIO_HEAT:
            risk_score += 3.0
            reasons.append(
                f"Portfolio heat {heat:.1%} exceeds limit {self.MAX_PORTFOLIO_HEAT:.1%}"
            )
        elif heat > self.MAX_PORTFOLIO_HEAT * 0.75:
            risk_score += 1.5
            reasons.append(f"Portfolio heat elevated ({heat:.1%})")

        # ── 4. Correlation to open positions ─────────────────────────────────
        corr_penalty = _correlation_penalty(symbol, open_positions)
        if corr_penalty > 0:
            risk_score += corr_penalty * 10
            reasons.append(
                f"Correlation overlap detected (penalty {corr_penalty:.2f})"
            )

        # ── 5. Strategy score quality ────────────────────────────────────────
        if strategy_score < 60:
            risk_score += 1.5
            reasons.append(f"Low strategy score ({strategy_score:.0f}/100)")

        # ── Decision ─────────────────────────────────────────────────────────
        risk_score = round(min(risk_score, 10.0), 2)
        approved = risk_score <= self.MAX_RISK_SCORE_APPROVE

        if not approved:
            reasons.insert(0, "BLOCKED: risk score too high")

        return {
            "agent": self.name,
            "symbol": symbol,
            "approved": approved,
            "risk_score": risk_score,
            "kelly_fraction": round(kelly, 4),
            "half_kelly_pct": round(half_kelly * 100, 2),
            "max_size_override": max_size_override,
            "rr_ratio": round(rr_ratio, 2) if rr_ratio else None,
            "portfolio_heat_pct": round(heat * 100, 2),
            "reason": "; ".join(reasons) if reasons else "Risk profile acceptable",
            "success": True,
        }
