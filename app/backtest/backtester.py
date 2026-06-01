import pandas as pd
from app.config import settings
from app.core.trade_management import init_state, on_candle_long
from app.backtest.simulator import OrderbookSimulator

def backtest_long(df: pd.DataFrame, plan_builder, warmup: int = 220, max_bars_in_trade: int = 72):
    simulator = OrderbookSimulator()
    trades = []
    in_trade = False
    state = None
    entry_ts = None

    for i in range(warmup, len(df)):
        dfx = df.iloc[: i+1]
        row = df.iloc[i].to_dict()

        if not in_trade:
            plan = plan_builder(dfx)
            if not plan:
                continue
            entry = float(plan["entry"])
            if float(row["high"]) >= entry:
                # Simulate fill price
                fill_price = simulator.simulate_fill(entry, float(row["high"]), float(row["low"]))
                
                stop = float(plan["stop"])
                tp1 = float(plan["tp1"]) if plan.get("tp1") is not None else None
                tp2 = float(plan["tp2"]) if plan.get("tp2") is not None else None
                state = init_state(fill_price, stop, tp1, tp2, units=1.0, max_bars=max_bars_in_trade)
                entry_ts = row["ts"]
                in_trade = True
                continue
        else:
            event = on_candle_long(state, row)
            if event["event"] in ("STOP", "TP2", "TIME_STOP"):
                exit_price = float(event["exit_price"])
                pnl = state["realized_pnl"] + (exit_price - state["entry"]) * state["remaining"]
                pnl = simulator.apply_costs(pnl, state["entry"], exit_price, 1.0)
                trades.append({"entry_ts": entry_ts, "exit_ts": row["ts"], "exit": event["event"], "pnl": pnl})
                in_trade = False
                state = None
                entry_ts = None

    return trades

