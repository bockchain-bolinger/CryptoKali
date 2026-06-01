from app.config import settings
from app.core.scoring import score_row
from app.core.risk import calc_position_size
from app.core.regime import mtf_filter

def build_trade_plan(df_signal, df_filter, venue: str, symbol: str, timeframe: str, strategy_payload: dict, extra: dict | None = None):
    latest = df_signal.iloc[-1].to_dict()

    if df_filter is not None:
        lf = df_filter.iloc[-1].to_dict()
        if not mtf_filter(lf, direction=strategy_payload.get("direction", "long")):
            return None

    scored = score_row(latest, extra=extra)

    entry = strategy_payload.get("entry")
    stop = strategy_payload.get("stop")
    units, risk_usd = calc_position_size(settings.ACCOUNT_EQUITY, settings.RISK_PCT_PER_TRADE, entry, stop)

    meta = {}
    meta.update(strategy_payload.get("meta", {}) or {})
    if extra:
        meta.update(extra)

    return {
        "venue": venue,
        "symbol": symbol,
        "strategy": strategy_payload["strategy"],
        "timeframe": timeframe,
        "score": scored["score"],
        "components": scored["components"],
        "entry": entry,
        "stop": stop,
        "tp1": strategy_payload.get("tp1"),
        "tp2": strategy_payload.get("tp2"),
        "position_size_units": units,
        "risk_usd": risk_usd,
        "tags": strategy_payload.get("tags", []),
        "meta": meta,
    }
