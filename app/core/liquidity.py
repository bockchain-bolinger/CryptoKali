from app.config import settings
from app.data.binance_spot_rest import depth as spot_depth
from app.data.binance_usdm_rest import depth as usdm_depth

def _parse_levels(levels):
    return [(float(p), float(q)) for p, q in levels]

def _walk_asks_for_notional(asks, notional_usd: float):
    remaining = notional_usd
    spent = 0.0
    for price, qty in asks:
        level_notional = price * qty
        take = min(level_notional, remaining)
        spent += take
        remaining -= take
        if remaining <= 1e-9:
            break
    filled = remaining <= 1e-9
    avg_price = spent / notional_usd if notional_usd > 0 else None
    return filled, avg_price

def orderbook_metrics(rest_symbol: str, market_type: str, notional_usd: float):
    ob = spot_depth(rest_symbol, limit=100) if market_type == "spot" else usdm_depth(rest_symbol, limit=100)
    bids = _parse_levels(ob.get("bids", []))
    asks = _parse_levels(ob.get("asks", []))
    if not bids or not asks:
        return {"ok": False}

    bid, ask = bids[0][0], asks[0][0]
    mid = (bid + ask) / 2.0
    spread_pct = (ask - bid) / mid

    filled, avg_price = _walk_asks_for_notional(asks, notional_usd)
    if avg_price is None:
        return {"ok": False}

    slippage_pct = (avg_price - mid) / mid if filled else 1.0
    return {"ok": True, "mid": mid, "spread_pct": spread_pct, "filled": filled, "slippage_pct": slippage_pct}

def liquidity_gate(metrics: dict) -> bool:
    if not metrics.get("ok"):
        return False
    if float(metrics["spread_pct"]) > settings.LIQ_MAX_SPREAD_PCT:
        return False
    if settings.LIQ_REQUIRE_FILLED_10K and not bool(metrics["filled"]):
        return False
    if float(metrics["slippage_pct"]) > settings.LIQ_MAX_SLIPPAGE_PCT_10K:
        return False
    return True
