def init_state(entry, stop, tp1, tp2, units, max_bars=72):
    return {
        "entry": float(entry),
        "stop": float(stop),
        "tp1": float(tp1) if tp1 is not None else None,
        "tp2": float(tp2) if tp2 is not None else None,
        "units": float(units) if units is not None else 1.0,
        "remaining": float(units) if units is not None else 1.0,
        "tp1_hit": False,
        "bars": 0,
        "max_bars": int(max_bars),
        "realized_pnl": 0.0,
    }

def on_candle_long(state: dict, candle: dict):
    state["bars"] += 1
    high = float(candle["high"])
    low = float(candle["low"])
    close = float(candle["close"])
    atr = float(candle.get("atr", 0.0) or 0.0)

    if state["bars"] >= state["max_bars"]:
        return {"event": "TIME_STOP", "exit_price": close}

    if low <= state["stop"]:
        return {"event": "STOP", "exit_price": state["stop"]}

    if state["tp2"] is not None and high >= state["tp2"]:
        return {"event": "TP2", "exit_price": state["tp2"]}

    if (not state["tp1_hit"]) and state["tp1"] is not None and high >= state["tp1"]:
        state["tp1_hit"] = True
        take = state["remaining"] * 0.40
        state["remaining"] -= take
        state["realized_pnl"] += (state["tp1"] - state["entry"]) * take
        state["stop"] = state["entry"]
        return {"event": "TP1_PARTIAL", "remaining": state["remaining"], "new_stop": state["stop"]}

    if state["tp1_hit"] and atr > 0:
        trail = close - 2.0 * atr
        if trail > state["stop"]:
            state["stop"] = trail
            return {"event": "TRAIL_UPDATE", "new_stop": state["stop"]}

    return {"event": "HOLD"}
