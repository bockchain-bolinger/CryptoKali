import pandas as pd

def relative_strength_change(df_asset: pd.DataFrame, df_btc: pd.DataFrame, bars: int = 168):
    a = df_asset[["ts","close"]].rename(columns={"close":"a"})
    b = df_btc[["ts","close"]].rename(columns={"close":"b"})
    m = a.merge(b, on="ts", how="inner")
    if len(m) <= bars:
        return None
    rs_now = m["a"].iloc[-1] / m["b"].iloc[-1]
    rs_then = m["a"].iloc[-bars] / m["b"].iloc[-bars]
    return float(rs_now / rs_then - 1.0)
