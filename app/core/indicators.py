import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange, BollingerBands

def _vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    pv = tp * df["volume"]
    return pv.rolling(50).sum() / df["volume"].rolling(50).sum()

def _supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.Series:
    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=period).average_true_range()
    hl2 = (df["high"] + df["low"]) / 2.0
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    st = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    st.iloc[0] = upperband.iloc[0]
    direction.iloc[0] = 1

    for i in range(1, len(df)):
        prev_st = st.iloc[i-1]
        prev_dir = direction.iloc[i-1]
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

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["ema20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(df["close"], window=200).ema_indicator()
    df["trend_up"] = (df["ema20"] > df["ema50"]).astype(int)

    df["rsi14"] = RSIIndicator(df["close"], window=14).rsi()

    atr = AverageTrueRange(df["high"], df["low"], df["close"], window=14)
    df["atr"] = atr.average_true_range()
    df["atr_pct"] = df["atr"] / df["close"]

    bb = BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_high"] = bb.bollinger_hband()
    df["bb_low"] = bb.bollinger_lband()

    adx = ADXIndicator(df["high"], df["low"], df["close"], window=14).adx()
    df["adx14"] = adx
    df["regime_trend"] = (df["adx14"] >= 20).astype(int)

    df["ret_1"] = df["close"].pct_change(1)
    df["ret_24"] = df["close"].pct_change(24)
    df["ret_168"] = df["close"].pct_change(168)

    df["vol_ma20"] = df["volume"].rolling(20).mean()
    df["vol_impulse"] = (df["volume"] / df["vol_ma20"]).replace([np.inf, -np.inf], np.nan)

    df["swing_low_20"] = df["low"].rolling(20).min()
    df["swing_high_20"] = df["high"].rolling(20).max()

    df["vwap50"] = _vwap(df)
    df["supertrend"] = _supertrend(df, period=10, multiplier=3.0)

    return df
