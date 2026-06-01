def calc_position_size(account_equity: float, risk_pct: float, entry: float, stop: float):
    if entry is None or stop is None:
        return None, None
    risk_usd = account_equity * risk_pct
    risk_per_unit = abs(entry - stop)
    if risk_per_unit <= 0:
        return None, None
    units = risk_usd / risk_per_unit
    return units, risk_usd

def tps_from_r(entry: float, stop: float, r1: float = 2.0, r2: float = 4.0, direction: str = "long"):
    if entry is None or stop is None:
        return None, None
    r = abs(entry - stop)
    if direction == "long":
        return entry + r1 * r, entry + r2 * r
    return entry - r1 * r, entry - r2 * r
