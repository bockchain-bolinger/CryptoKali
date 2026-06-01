import json
from datetime import datetime, timezone
from app.config import settings
from app.db import connect
from app.data.fetchers import (
    fetch_ohlcv, build_universe_spot, build_universe_usdm,
    spot_to_rest_symbol, futures_to_rest_symbol
)
from app.core.indicators import add_indicators
from app.core.liquidity import orderbook_metrics, liquidity_gate
from app.core.engine import build_trade_plan
from app.core.strategies import SPOT_STRATS, s5_derivatives_squeeze, s6_rotation, s3_catalyst_proxy
from app.core.derivatives_features import derivatives_snapshot
from app.core.catalyst import poll_binance_announcements, catalyst_score_for_symbol
from app.live.alerts import can_send, mark_sent, send_telegram, send_discord, send_webhook

def _now():
    return datetime.now(timezone.utc).isoformat()

def store_scan(plan: dict):
    con = connect()
    cur = con.cursor()
    cur.execute(
        """INSERT INTO scans(ts, venue, symbol, timeframe, strategy, score, entry, stop, tp1, tp2, tags, meta_json)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            _now(), plan["venue"], plan["symbol"], plan["timeframe"], plan["strategy"], plan["score"],
            plan.get("entry"), plan.get("stop"), plan.get("tp1"), plan.get("tp2"),
            ",".join(plan.get("tags", [])),
            json.dumps({"components": plan.get("components", {}), "meta": plan.get("meta", {})})
        )
    )
    con.commit()
    con.close()

def _emit_alert(plan: dict):
    text = (
        f"[CryptoKali][{plan['venue']}] {plan['symbol']} | {plan['strategy']} | score={plan['score']}\n"
        f"Entry: {plan['entry']:.6g}  SL: {plan['stop']:.6g}\n"
        f"TP1: {plan['tp1']:.6g}  TP2: {plan['tp2']:.6g}\n"
        f"Units: {plan.get('position_size_units', 0) or 0:.4g}  Risk$: {plan.get('risk_usd', 0) or 0:.2f}\n"
        f"Tags: {', '.join(plan.get('tags', []))}"
    )
    send_telegram(text)
    send_discord(text)
    send_webhook(plan)

def scan_once():
    results = []
    poll_binance_announcements()

    btc_sig = add_indicators(fetch_ohlcv("BTC/USDT", settings.TF_SIGNAL, settings.LIMIT_SIGNAL, "spot")).dropna()
    btc_flt = add_indicators(fetch_ohlcv("BTC/USDT", settings.TF_FILTER, settings.LIMIT_FILTER, "spot")).dropna()

    for sym in build_universe_spot():
        df_sig = add_indicators(fetch_ohlcv(sym, settings.TF_SIGNAL, settings.LIMIT_SIGNAL, "spot")).dropna()
        if len(df_sig) < 250:
            continue
        df_flt = add_indicators(fetch_ohlcv(sym, settings.TF_FILTER, settings.LIMIT_FILTER, "spot")).dropna()
        if len(df_flt) < 150:
            continue

        rest = spot_to_rest_symbol(sym)
        obm = orderbook_metrics(rest, "spot", settings.LIQ_TEST_NOTIONAL_USD)
        if not liquidity_gate(obm):
            continue

        extra_liq = {"spread_pct": obm["spread_pct"], "slippage_pct": obm["slippage_pct"]}

        for strat in SPOT_STRATS:
            payload = strat(df_sig)
            if not payload:
                continue
            plan = build_trade_plan(df_sig, df_flt, "SPOT", sym, settings.TF_SIGNAL, payload, extra=extra_liq)
            if not plan:
                continue
            results.append(plan)
            store_scan(plan)
            if plan["score"] >= 75 and can_send(plan["venue"], sym, plan["strategy"]):
                _emit_alert(plan)
                mark_sent(plan["venue"], sym, plan["strategy"])

        # Catalyst strategy
        cscore = catalyst_score_for_symbol(sym)
        cat_payload = s3_catalyst_proxy(df_sig, catalyst_score=cscore)
        if cat_payload:
            plan = build_trade_plan(df_sig, df_flt, "SPOT", sym, settings.TF_SIGNAL, cat_payload, extra=extra_liq | {"catalyst_score": cscore})
            if plan:
                results.append(plan)
                store_scan(plan)
                if plan["score"] >= 75 and can_send(plan["venue"], sym, plan["strategy"]):
                    _emit_alert(plan)
                    mark_sent(plan["venue"], sym, plan["strategy"])

        rot_payload = s6_rotation(df_sig, btc_sig)
        if rot_payload:
            plan = build_trade_plan(df_sig, df_flt, "SPOT", sym, settings.TF_SIGNAL, rot_payload, extra=extra_liq)
            if plan:
                results.append(plan)
                store_scan(plan)
                if plan["score"] >= 75 and can_send(plan["venue"], sym, plan["strategy"]):
                    _emit_alert(plan)
                    mark_sent(plan["venue"], sym, plan["strategy"])

    for sym in build_universe_usdm():
        df_sig = add_indicators(fetch_ohlcv(sym, settings.TF_SIGNAL, settings.LIMIT_SIGNAL, "usdm")).dropna()
        if len(df_sig) < 250:
            continue
        df_flt = add_indicators(fetch_ohlcv(sym, settings.TF_FILTER, settings.LIMIT_FILTER, "usdm")).dropna()
        if len(df_flt) < 150:
            continue

        rest = futures_to_rest_symbol(sym)
        obm = orderbook_metrics(rest, "usdm", settings.LIQ_TEST_NOTIONAL_USD)
        if not liquidity_gate(obm):
            continue

        payload = s5_derivatives_squeeze(df_sig, rest)
        if not payload:
            continue

        snap = derivatives_snapshot(rest)
        extra = {"spread_pct": obm["spread_pct"], "slippage_pct": obm["slippage_pct"]} | snap
        plan = build_trade_plan(df_sig, df_flt, "FUTURES", sym, settings.TF_SIGNAL, payload, extra=extra)
        if not plan:
            continue

        results.append(plan)
        store_scan(plan)
        if plan["score"] >= 75 and can_send(plan["venue"], sym, plan["strategy"]):
            _emit_alert(plan)
            mark_sent(plan["venue"], sym, plan["strategy"])

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[: settings.TOP_N]
