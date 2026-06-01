import numpy as np

def clamp(x, lo=0.0, hi=1.0):
    return float(max(lo, min(hi, x)))

def score_row(latest: dict, extra: dict | None = None) -> dict:
    mom = 0.0
    mom += clamp((float(latest.get("ret_24", 0.0)) + 0.10) / 0.20) * 0.55
    mom += clamp((float(latest.get("ret_168", 0.0)) + 0.30) / 0.60) * 0.45

    trend = 1.0 if int(latest.get("trend_up", 0)) == 1 else 0.0

    vol_imp = latest.get("vol_impulse", np.nan)
    volq = clamp((float(vol_imp) - 1.0) / 2.0) if vol_imp == vol_imp else 0.0

    atr_pct = float(latest.get("atr_pct", 0.0))
    vola = clamp((atr_pct - 0.01) / 0.09)

    adx = float(latest.get("adx14", 0.0))
    trend_strength = clamp((adx - 15.0) / 20.0)

    rsi = float(latest.get("rsi14", 50.0))
    penalty = 0.0
    if rsi > 82: penalty += 0.12
    if rsi < 18: penalty += 0.10
    if atr_pct > 0.12: penalty += 0.18

    deriv_bonus = 0.0
    liq_penalty = 0.0
    if extra:
        fz = float(extra.get("funding_z", 0.0))
        if fz < -2.0: deriv_bonus += 0.05
        if fz > 2.0: deriv_bonus -= 0.03
        spread = float(extra.get("spread_pct", 0.0))
        slip = float(extra.get("slippage_pct", 0.0))
        if spread > 0.002: liq_penalty += 0.08
        if slip > 0.003: liq_penalty += 0.08

    raw = 0.28*mom + 0.15*trend + 0.20*trend_strength + 0.22*volq + 0.15*vola + deriv_bonus
    final = clamp(raw - penalty - liq_penalty) * 100.0

    return {
        "score": round(final, 2),
        "components": {
            "momentum": round(mom, 3),
            "trend": round(trend, 3),
            "trend_strength": round(trend_strength, 3),
            "volume_quality": round(volq, 3),
            "volatility": round(vola, 3),
            "penalty": round(penalty, 3),
            "liq_penalty": round(liq_penalty, 3),
            "deriv_bonus": round(deriv_bonus, 3),
        }
    }
