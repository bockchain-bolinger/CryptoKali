"""
market_analyst.py – MarketAnalystAgent for CryptoKali.

When OPENAI_API_KEY is set the agent calls GPT-4o with a structured-output
prompt and returns a JSON-parsed result.

Without an API key the agent falls back to a deterministic rule-based analysis
using EMA trend, RSI state, volume impulse, ADX regime, SuperTrend, MACD, and
Bollinger-Band position.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# ── Optional OpenAI import ───────────────────────────────────────────────────
try:
    from openai import OpenAI  # type: ignore
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val) -> Optional[float]:
    """Convert a value to float, returning None on failure."""
    try:
        v = float(val)
        return None if (np.isnan(v) or np.isinf(v)) else round(v, 8)
    except (TypeError, ValueError):
        return None


def _last(series: pd.Series, default=None):
    """Return the last non-NaN value of a Series or `default`."""
    s = series.dropna()
    return s.iloc[-1] if len(s) else default


def _key_levels(df: pd.DataFrame, n: int = 5) -> List[float]:
    """
    Return the most recent support / resistance levels from:
    swing_low_20, swing_high_20, pivot points (if available), and
    Bollinger Bands.
    """
    levels: List[float] = []
    for col in ("swing_low_20", "swing_high_20", "bb_high", "bb_low",
                "r1", "s1", "r2", "s2"):
        if col in df.columns:
            v = _safe_float(_last(df[col]))
            if v is not None:
                levels.append(v)
    return sorted(set(round(l, 6) for l in levels))[:n]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class MarketAnalystAgent(BaseAgent):
    """
    Analyses OHLCV + indicator data for a single symbol and returns a
    structured market assessment.
    """

    @property
    def name(self) -> str:
        return "MarketAnalystAgent"

    @property
    def description(self) -> str:
        return (
            "Analyses trend, momentum, volume and key levels for a symbol. "
            "Uses GPT-4o when OPENAI_API_KEY is set, otherwise falls back "
            "to deterministic rule-based analysis."
        )

    # ── Entry point ──────────────────────────────────────────────────────────

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parameters
        ----------
        context : dict
            Required keys:
              • ``symbol`` – e.g. "BTC/USDT"
              • ``df``     – pandas DataFrame with indicators already applied

        Returns
        -------
        dict with keys: symbol, trend, bias, key_levels, summary,
                        confidence, agent
        """
        symbol: str = context.get("symbol", "UNKNOWN")
        df: Optional[pd.DataFrame] = context.get("df")

        if df is None or df.empty:
            return self._error_result(f"No data provided for {symbol}")

        api_key = os.getenv("OPENAI_API_KEY", "")

        if api_key and _OPENAI_AVAILABLE:
            try:
                return self._llm_analyze(symbol, df, api_key)
            except Exception as exc:
                logger.warning(
                    "GPT-4o call failed for %s (%s); falling back to rules.",
                    symbol, exc,
                )

        return self._rule_analyze(symbol, df)

    # ── Rule-based fallback ──────────────────────────────────────────────────

    def _rule_analyze(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Deterministic rule-based market analysis."""
        last = df.iloc[-1]

        # ── Trend ──────────────────────────────────────────────────────────
        ema20 = _safe_float(last.get("ema20"))
        ema50 = _safe_float(last.get("ema50"))
        ema200 = _safe_float(last.get("ema200"))
        close = _safe_float(last.get("close"))
        supertrend = _safe_float(last.get("supertrend"))

        trend_votes = 0
        trend_total = 0

        if ema20 and ema50:
            trend_total += 1
            if ema20 > ema50:
                trend_votes += 1
        if ema50 and ema200:
            trend_total += 1
            if ema50 > ema200:
                trend_votes += 1
        if close and supertrend:
            trend_total += 1
            if close > supertrend:
                trend_votes += 1

        trend_ratio = trend_votes / trend_total if trend_total else 0.5
        if trend_ratio >= 0.67:
            trend = "uptrend"
        elif trend_ratio <= 0.33:
            trend = "downtrend"
        else:
            trend = "sideways"

        # ── RSI state ──────────────────────────────────────────────────────
        rsi = _safe_float(last.get("rsi14"))
        if rsi is not None:
            if rsi >= 70:
                rsi_label = "overbought"
            elif rsi <= 30:
                rsi_label = "oversold"
            elif rsi > 55:
                rsi_label = "bullish"
            elif rsi < 45:
                rsi_label = "bearish"
            else:
                rsi_label = "neutral"
        else:
            rsi_label = "unknown"

        # ── MACD ───────────────────────────────────────────────────────────
        macd_hist = _safe_float(last.get("macd_hist"))
        macd_signal_bias = (
            "bullish" if macd_hist and macd_hist > 0
            else "bearish" if macd_hist and macd_hist < 0
            else "neutral"
        )

        # ── Volume ─────────────────────────────────────────────────────────
        vol_impulse = _safe_float(last.get("vol_impulse"))
        if vol_impulse is not None:
            if vol_impulse >= 2.0:
                vol_label = "very_high"
            elif vol_impulse >= 1.5:
                vol_label = "high"
            elif vol_impulse >= 0.8:
                vol_label = "normal"
            else:
                vol_label = "low"
        else:
            vol_label = "unknown"

        # ── ADX regime ─────────────────────────────────────────────────────
        adx = _safe_float(last.get("adx14"))
        regime = "trending" if (adx and adx >= 25) else "ranging"

        # ── Overall bias ───────────────────────────────────────────────────
        bias_score = 0
        if trend == "uptrend":
            bias_score += 2
        elif trend == "downtrend":
            bias_score -= 2
        if rsi_label in ("bullish", "oversold"):
            bias_score += 1
        elif rsi_label in ("bearish", "overbought"):
            bias_score -= 1
        if macd_signal_bias == "bullish":
            bias_score += 1
        elif macd_signal_bias == "bearish":
            bias_score -= 1

        if bias_score >= 2:
            bias = "bullish"
        elif bias_score <= -2:
            bias = "bearish"
        else:
            bias = "neutral"

        confidence = min(0.5 + abs(bias_score) * 0.1, 0.95)

        summary = (
            f"{symbol} is in a {trend} ({regime} regime). "
            f"RSI={rsi:.1f} ({rsi_label}), "
            f"MACD histogram {macd_signal_bias}, "
            f"Volume impulse={vol_impulse:.2f}x ({vol_label}). "
            f"Overall bias: {bias.upper()}."
        ) if rsi and vol_impulse else (
            f"{symbol} – insufficient data for full analysis. "
            f"Trend: {trend}, Bias: {bias}."
        )

        return {
            "agent": self.name,
            "symbol": symbol,
            "trend": trend,
            "regime": regime,
            "bias": bias,
            "rsi_state": rsi_label,
            "macd_bias": macd_signal_bias,
            "volume": vol_label,
            "key_levels": _key_levels(df),
            "summary": summary,
            "confidence": round(confidence, 2),
            "source": "rules",
            "success": True,
        }

    # ── LLM path ─────────────────────────────────────────────────────────────

    def _build_snapshot(self, df: pd.DataFrame) -> str:
        """Serialise the last 3 candles + key indicators to a compact string."""
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last

        cols = [
            "open", "high", "low", "close", "volume",
            "ema20", "ema50", "ema200", "rsi14", "adx14",
            "macd_line", "macd_signal", "macd_hist",
            "stoch_rsi_k", "stoch_rsi_d",
            "cci14", "williams_r", "mfi14",
            "bb_high", "bb_low", "atr", "supertrend",
            "vol_impulse", "obv", "cvd",
        ]
        snap: Dict[str, Any] = {}
        for col in cols:
            if col in last.index:
                v = _safe_float(last[col])
                if v is not None:
                    snap[col] = v
        snap["prev_close"] = _safe_float(prev.get("close"))
        snap["key_levels"] = _key_levels(df)
        return json.dumps(snap, indent=2)

    def _llm_analyze(
        self, symbol: str, df: pd.DataFrame, api_key: str
    ) -> Dict[str, Any]:
        """Call GPT-4o with a structured JSON output prompt."""
        client = OpenAI(api_key=api_key)
        snapshot = self._build_snapshot(df)

        system_prompt = (
            "You are an expert cryptocurrency technical analyst. "
            "You receive a JSON snapshot of the latest market data and indicators "
            "for a crypto symbol and must respond ONLY with a valid JSON object "
            "(no markdown, no prose) with exactly these keys:\n"
            "  trend        : 'uptrend' | 'downtrend' | 'sideways'\n"
            "  bias         : 'bullish' | 'bearish' | 'neutral'\n"
            "  key_levels   : list of up to 5 important price levels (floats)\n"
            "  summary      : concise 2-3 sentence analysis string\n"
            "  confidence   : float 0.0 – 1.0\n"
            "  regime       : 'trending' | 'ranging'\n"
        )

        user_msg = (
            f"Symbol: {symbol}\n\nIndicator snapshot:\n{snapshot}\n\n"
            "Respond only with the JSON object described."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=512,
            temperature=0.2,
        )

        raw = response.choices[0].message.content.strip()
        # Strip potential markdown code fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed: Dict[str, Any] = json.loads(raw)

        return {
            "agent": self.name,
            "symbol": symbol,
            "trend": parsed.get("trend", "sideways"),
            "regime": parsed.get("regime", "ranging"),
            "bias": parsed.get("bias", "neutral"),
            "key_levels": parsed.get("key_levels", _key_levels(df)),
            "summary": parsed.get("summary", ""),
            "confidence": float(parsed.get("confidence", 0.5)),
            "source": "gpt-4o",
            "success": True,
        }
