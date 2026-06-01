import numpy as np
from app.data.binance_usdm_rest import funding_rate_history, open_interest, all_force_orders

def _zscore(vals):
    x = np.array(vals, dtype=float)
    if len(x) < 10:
        return 0.0
    m = x.mean()
    s = x.std() if x.std() > 1e-12 else 1.0
    return float((x[-1] - m) / s)

def derivatives_snapshot(rest_symbol: str) -> dict:
    fr = funding_rate_history(rest_symbol, limit=50)
    fr_vals = [float(i.get("fundingRate", 0.0)) for i in fr if "fundingRate" in i]
    fr_last = float(fr_vals[-1]) if fr_vals else 0.0
    fr_z = _zscore(fr_vals) if fr_vals else 0.0

    oi = open_interest(rest_symbol)
    oi_val = float(oi.get("openInterest", 0.0))

    fo = all_force_orders(symbol=rest_symbol, limit=100)
    liq_notional = 0.0
    liq_count = 0
    for x in fo if isinstance(fo, list) else []:
        p = float(x.get("price", 0.0) or 0.0)
        q = float(x.get("origQty", 0.0) or x.get("qty", 0.0) or 0.0)
        liq_notional += p * q
        liq_count += 1

    return {
        "funding_last": fr_last,
        "funding_z": fr_z,
        "open_interest": oi_val,
        "liq_count_100": liq_count,
        "liq_notional_100": liq_notional,
    }
