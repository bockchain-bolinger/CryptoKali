def regime_gate(latest: dict, want: str) -> bool:
    is_trend = int(latest.get("regime_trend", 0)) == 1
    if want == "trend":
        return is_trend
    if want == "range":
        return not is_trend
    return True

def mtf_filter(latest_filter: dict, direction: str = "long") -> bool:
    if direction == "long":
        return int(latest_filter.get("trend_up", 0)) == 1 and float(latest_filter.get("close", 0.0)) >= float(latest_filter.get("ema50", 0.0))
    return True
