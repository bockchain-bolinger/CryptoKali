from app.core.risk import tps_from_r
from app.core.regime import regime_gate
from app.core.derivatives_features import derivatives_snapshot
from app.core.rotation import relative_strength_change

def _last(df):
    return df.iloc[-1].to_dict()

def s1_momentum_breakout(df):
    x = _last(df)
    if not regime_gate(x, "trend"):
        return None
    if int(x["trend_up"]) != 1:
        return None
    if float(x.get("vol_impulse", 0)) < 1.6:
        return None
    if float(x.get("ret_24", 0)) < 0.03:
        return None
    rsi = float(x.get("rsi14", 50))
    if not (55 <= rsi <= 75):
        return None
    entry = float(x["swing_high_20"])
    stop = float(x["swing_low_20"])
    tp1, tp2 = tps_from_r(entry, stop, 2.0, 4.0, "long")
    return {"strategy":"momentum_breakout","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["momentum_breakout","trend_following"]}

def s2_mean_reversion(df):
    x = _last(df)
    if not regime_gate(x, "range"):
        return None
    rsi = float(x.get("rsi14", 50))
    if rsi > 28:
        return None
    entry = float(x["bb_low"])
    stop = float(x["swing_low_20"])
    tp1, tp2 = tps_from_r(entry, stop, 1.5, 3.0, "long")
    return {"strategy":"mean_reversion","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["mean_reversion","oversold_bounce"]}

def s3_catalyst_proxy(df, catalyst_score: float = 0.0):
    x = _last(df)
    vol_imp = float(x.get("vol_impulse", 0))
    r24 = float(x.get("ret_24", 0))
    if not (vol_imp >= 2.0 and 0.02 <= r24 <= 0.12):
        return None
    if catalyst_score < 0.5:
        return None
    entry = float(x["close"])
    stop = float(x["swing_low_20"])
    tp1, tp2 = tps_from_r(entry, stop, 2.0, 5.0, "long")
    return {"strategy":"catalyst_play","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["catalyst_play","event_driven"],"meta":{"catalyst_score": catalyst_score}}

def s4_lowcap_volatility(df):
    x = _last(df)
    atr_pct = float(x.get("atr_pct", 0))
    if atr_pct < 0.08:
        return None
    if float(x.get("vol_impulse", 0)) < 2.5:
        return None
    entry = float(x["close"]) * 0.985
    stop = float(x["close"]) - 2.0 * float(x["atr"])
    tp1, tp2 = tps_from_r(entry, stop, 2.0, 4.0, "long")
    return {"strategy":"lowcap_volatility","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["high_volatility_high_risk","lowcap_gamble"],"meta":{"position_sizing":"reduce"}}

def s5_derivatives_squeeze(df, fut_rest_symbol: str):
    x = _last(df)
    if not regime_gate(x, "trend"):
        return None
    snap = derivatives_snapshot(fut_rest_symbol)
    funding_z = float(snap["funding_z"])
    liq_count = int(snap["liq_count_100"])
    oi = float(snap["open_interest"])

    if funding_z > -1.5:
        return None
    if liq_count < 5:
        return None
    if oi <= 0:
        return None

    entry = float(x["swing_high_20"])
    stop = float(x["swing_low_20"])
    tp1, tp2 = tps_from_r(entry, stop, 2.0, 3.5, "long")
    return {"strategy":"derivatives_squeeze","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,
            "tags":["derivatives_setup","squeeze_risk"],"meta": snap}

def s6_rotation(df_asset, df_btc):
    x = _last(df_asset)
    if int(x.get("trend_up", 0)) != 1:
        return None
    rs7 = relative_strength_change(df_asset, df_btc, bars=168)
    if rs7 is None or rs7 < 0.05:
        return None
    entry = float(x["close"])
    stop = float(x["ema50"])
    tp1, tp2 = tps_from_r(entry, stop, 1.8, 3.2, "long")
    return {"strategy":"rotation_play","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["rotation_play","sector_strength"],"meta":{"rs7": rs7}}

def s7_accumulation_breakout(df):
    x = _last(df)
    if float(x.get("atr_pct", 1)) > 0.045:
        return None
    if float(x.get("vol_impulse", 0)) < 1.8:
        return None
    entry = float(x["swing_high_20"])
    stop = float(x["swing_low_20"])
    tp1, tp2 = tps_from_r(entry, stop, 2.5, 5.0, "long")
    return {"strategy":"accumulation_breakout","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["accumulation","base_breakout"]}

SPOT_STRATS = [s1_momentum_breakout, s2_mean_reversion, s4_lowcap_volatility, s7_accumulation_breakout]
