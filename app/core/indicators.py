"""
indicators.py – Full technical-indicator library for CryptoKali.

Includes:
  Classic : EMA(20/50/200), RSI(14), ATR(14), Bollinger Bands(20,2),
            ADX(14), VWAP(50), SuperTrend(10, 3)
  New     : MACD(12,26,9), Stochastic-RSI(14,3,3), CCI(14),
            Williams %R(14), OBV, MFI(14), Ichimoku Cloud(9,26,52),
            Heikin-Ashi, CVD, Pivot Points (daily standard)
  Utils   : detect_divergence(df, indicator_col, price_col, window=5)
"""

import logging

import numpy as np
import pandas as pd
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import ADXIndicator, EMAIndicator, MACD, CCIIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from ta.volume import MFIIndicator, OnBalanceVolumeIndicator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vwap(df: pd.DataFrame, window: int = 50) -> pd.Series:
    """Rolling VWAP over `window` bars."""
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = tp * df["volume"]
    return pv.rolling(window).sum() / df["volume"].rolling(window).sum()


def _supertrend(
    df: pd.DataFrame, period: int = 10, multiplier: float = 3.0
) -> pd.Series:
    """SuperTrend indicator – returns the trailing stop series."""
    atr = AverageTrueRange(
        df["high"], df["low"], df["close"], window=period
    ).average_true_range()
    hl2 = (df["high"] + df["low"]) / 2.0
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    st.iloc[0] = upperband.iloc[0]
    direction.iloc[0] = 1

    for i in range(1, len(df)):
        prev_st = st.iloc[i - 1]
        prev_dir = direction.iloc[i - 1]
        close = df["close"].iloc[i]
        ub = upperband.iloc[i]
        lb = lowerband.iloc[i]

        if close > prev_st:
            direction.iloc[i] = 1
        elif close < prev_st:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = prev_dir

        if direction.iloc[i] == 1:
            st.iloc[i] = min(ub, prev_st) if prev_dir == 1 else ub
        else:
            st.iloc[i] = max(lb, prev_st) if prev_dir == -1 else lb

    return st


# ---------------------------------------------------------------------------
# New indicator helpers
# ---------------------------------------------------------------------------

def _macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """Return DataFrame with columns: macd_line, macd_signal, macd_hist."""
    macd_obj = MACD(close, window_slow=slow, window_fast=fast, window_sign=signal)
    return pd.DataFrame(
        {
            "macd_line": macd_obj.macd(),
            "macd_signal": macd_obj.macd_signal(),
            "macd_hist": macd_obj.macd_diff(),
        },
        index=close.index,
    )


def _stoch_rsi(
    close: pd.Series,
    window: int = 14,
    smooth1: int = 3,
    smooth2: int = 3,
) -> pd.DataFrame:
    """Return DataFrame with columns: stoch_rsi_k, stoch_rsi_d."""
    srsi = StochRSIIndicator(close, window=window, smooth1=smooth1, smooth2=smooth2)
    return pd.DataFrame(
        {
            "stoch_rsi_k": srsi.stochrsi_k() * 100,
            "stoch_rsi_d": srsi.stochrsi_d() * 100,
        },
        index=close.index,
    )


def _cci(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Commodity Channel Index."""
    return CCIIndicator(df["high"], df["low"], df["close"], window=window).cci()


def _williams_r(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Williams %R."""
    highest_high = df["high"].rolling(window).max()
    lowest_low = df["low"].rolling(window).min()
    wr = -100 * (highest_high - df["close"]) / (highest_high - lowest_low)
    return wr


def _obv(df: pd.DataFrame) -> pd.Series:
    """On-Balance Volume."""
    return OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()


def _mfi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Money Flow Index."""
    return MFIIndicator(
        df["high"], df["low"], df["close"], df["volume"], window=window
    ).money_flow_index()


def _ichimoku(
    df: pd.DataFrame,
    tenkan: int = 9,
    kijun: int = 26,
    senkou_b_period: int = 52,
) -> pd.DataFrame:
    """
    Ichimoku Cloud.

    Returns DataFrame with:
        tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span
    """
    def mid(high, low, win):
        return (high.rolling(win).max() + low.rolling(win).min()) / 2

    tenkan_sen = mid(df["high"], df["low"], tenkan)
    kijun_sen = mid(df["high"], df["low"], kijun)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
    senkou_span_b = mid(df["high"], df["low"], senkou_b_period).shift(kijun)
    chikou_span = df["close"].shift(-kijun)

    return pd.DataFrame(
        {
            "ichimoku_tenkan": tenkan_sen,
            "ichimoku_kijun": kijun_sen,
            "ichimoku_span_a": senkou_span_a,
            "ichimoku_span_b": senkou_span_b,
            "ichimoku_chikou": chikou_span,
        },
        index=df.index,
    )


def _heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Heikin-Ashi candles.

    Returns DataFrame with: ha_open, ha_close, ha_high, ha_low
    """
    ha_close = (df["open"] + df["high"] + df["low"] + df["close"]) / 4

    ha_open = pd.Series(index=df.index, dtype=float)
    ha_open.iloc[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2
    for i in range(1, len(df)):
        ha_open.iloc[i] = (ha_open.iloc[i - 1] + ha_close.iloc[i - 1]) / 2

    ha_high = pd.concat([df["high"], ha_open, ha_close], axis=1).max(axis=1)
    ha_low = pd.concat([df["low"], ha_open, ha_close], axis=1).min(axis=1)

    return pd.DataFrame(
        {
            "ha_open": ha_open,
            "ha_close": ha_close,
            "ha_high": ha_high,
            "ha_low": ha_low,
        },
        index=df.index,
    )


def _cvd(df: pd.DataFrame) -> pd.Series:
    """
    Cumulative Volume Delta (approximation).

    Buy volume  ≈ volume × (close - low) / (high - low)
    Sell volume ≈ volume × (high - close) / (high - low)
    CVD         = cumsum(buy_vol - sell_vol)
    """
    hl_range = (df["high"] - df["low"]).replace(0, np.nan)
    buy_vol = df["volume"] * (df["close"] - df["low"]) / hl_range
    sell_vol = df["volume"] * (df["high"] - df["close"]) / hl_range
    delta = (buy_vol - sell_vol).fillna(0)
    return delta.cumsum()


def _pivot_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standard Pivot Points based on the previous candle (acts as "previous day"
    when using daily data, or previous bar on any timeframe).

    Columns: pivot, r1, r2, r3, s1, s2, s3
    """
    prev_high = df["high"].shift(1)
    prev_low = df["low"].shift(1)
    prev_close = df["close"].shift(1)

    pivot = (prev_high + prev_low + prev_close) / 3
    r1 = 2 * pivot - prev_low
    s1 = 2 * pivot - prev_high
    r2 = pivot + (prev_high - prev_low)
    s2 = pivot - (prev_high - prev_low)
    r3 = prev_high + 2 * (pivot - prev_low)
    s3 = prev_low - 2 * (prev_high - pivot)

    return pd.DataFrame(
        {
            "pivot": pivot,
            "r1": r1,
            "r2": r2,
            "r3": r3,
            "s1": s1,
            "s2": s2,
            "s3": s3,
        },
        index=df.index,
    )


# ---------------------------------------------------------------------------
# Divergence detection
# ---------------------------------------------------------------------------

def detect_divergence(
    df: pd.DataFrame,
    indicator_col: str,
    price_col: str = "close",
    window: int = 5,
) -> str | None:
    """
    Detect regular bullish or bearish divergence over the last `window` bars.

    Bullish  divergence: price makes lower low  but indicator makes higher low.
    Bearish  divergence: price makes higher high but indicator makes lower high.

    Returns 'bullish', 'bearish', or None.
    """
    try:
        if indicator_col not in df.columns or price_col not in df.columns:
            return None
        if len(df) < window * 2:
            return None

        recent = df.tail(window * 2)
        mid = window  # split point

        first_half = recent.iloc[:mid]
        second_half = recent.iloc[mid:]

        price_first_low = first_half[price_col].min()
        price_second_low = second_half[price_col].min()
        ind_first_low = first_half[indicator_col].min()
        ind_second_low = second_half[indicator_col].min()

        price_first_high = first_half[price_col].max()
        price_second_high = second_half[price_col].max()
        ind_first_high = first_half[indicator_col].max()
        ind_second_high = second_half[indicator_col].max()

        # Bullish divergence
        if price_second_low < price_first_low and ind_second_low > ind_first_low:
            return "bullish"

        # Bearish divergence
        if price_second_high > price_first_high and ind_second_high < ind_first_high:
            return "bearish"

        return None
    except Exception as exc:
        logger.debug("detect_divergence error: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute and attach all technical indicators to a copy of `df`.

    Input columns required: open, high, low, close, volume
    """
    df = df.copy()

    # ── Classic EMAs ────────────────────────────────────────────────────────
    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(df["close"], window=200).ema_indicator()
    df["trend_up"] = (df["ema20"] > df["ema50"]).astype(int)

    # ── RSI ─────────────────────────────────────────────────────────────────
    df["rsi14"] = RSIIndicator(df["close"], window=14).rsi()

    # ── ATR ─────────────────────────────────────────────────────────────────
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=14)
    df["atr"] = atr.average_true_range()
    df["atr_pct"] = df["atr"] / df["close"]

    # ── Bollinger Bands ──────────────────────────────────────────────────────
    bb = BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()
    df["bb_pct"] = bb.bollinger_pband()   # %B

    # ── ADX ─────────────────────────────────────────────────────────────────
    adx_obj = ADXIndicator(df["high"], df["low"], df["close"], window=14)
    df["adx14"] = adx_obj.adx()
    df["regime_trend"] = (df["adx14"] >= 20).astype(int)

    # ── Return features ──────────────────────────────────────────────────────
    df["ret_1"] = df["close"].pct_change(1)
    df["ret_24"] = df["close"].pct_change(24)
    df["ret_168"] = df["close"].pct_change(168)

    # ── Volume features ──────────────────────────────────────────────────────
    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_impulse"] = (df["volume"] / df["vol_ma20"]).replace(
        [np.inf, -np.inf], np.nan
    )

    # ── Swing levels ─────────────────────────────────────────────────────────
    df["swing_low_20"] = df["low"].rolling(20).min()
    df["swing_high_20"] = df["high"].rolling(20).max()

    # ── VWAP & SuperTrend ────────────────────────────────────────────────────
    df["vwap50"] = _vwap(df, window=50)
    df["supertrend"] = _supertrend(df, period=10, multiplier=3.0)

    # ── MACD ─────────────────────────────────────────────────────────────────
    try:
        macd_df = _macd(df["close"])
        df = pd.concat([df, macd_df], axis=1)
    except Exception as exc:
        logger.warning("MACD computation failed: %s", exc)

    # ── Stochastic RSI ───────────────────────────────────────────────────────
    try:
        srsi_df = _stoch_rsi(df["close"])
        df = pd.concat([df, srsi_df], axis=1)
    except Exception as exc:
        logger.warning("StochRSI computation failed: %s", exc)

    # ── CCI ──────────────────────────────────────────────────────────────────
    try:
        df["cci14"] = _cci(df, window=14)
    except Exception as exc:
        logger.warning("CCI computation failed: %s", exc)

    # ── Williams %R ──────────────────────────────────────────────────────────
    try:
        df["williams_r"] = _williams_r(df, window=14)
    except Exception as exc:
        logger.warning("Williams %%R computation failed: %s", exc)

    # ── OBV ──────────────────────────────────────────────────────────────────
    try:
        df["obv"] = _obv(df)
    except Exception as exc:
        logger.warning("OBV computation failed: %s", exc)

    # ── MFI ──────────────────────────────────────────────────────────────────
    try:
        df["mfi14"] = _mfi(df, window=14)
    except Exception as exc:
        logger.warning("MFI computation failed: %s", exc)

    # ── Ichimoku Cloud ───────────────────────────────────────────────────────
    try:
        ichi_df = _ichimoku(df)
        df = pd.concat([df, ichi_df], axis=1)
    except Exception as exc:
        logger.warning("Ichimoku computation failed: %s", exc)

    # ── Heikin-Ashi ──────────────────────────────────────────────────────────
    try:
        ha_df = _heikin_ashi(df)
        df = pd.concat([df, ha_df], axis=1)
    except Exception as exc:
        logger.warning("Heikin-Ashi computation failed: %s", exc)

    # ── CVD ──────────────────────────────────────────────────────────────────
    try:
        df["cvd"] = _cvd(df)
    except Exception as exc:
        logger.warning("CVD computation failed: %s", exc)

    # ── Pivot Points ─────────────────────────────────────────────────────────
    try:
        piv_df = _pivot_points(df)
        df = pd.concat([df, piv_df], axis=1)
    except Exception as exc:
        logger.warning("Pivot Points computation failed: %s", exc)

    return df
