import numpy as np

def compute_metrics(pnls):
    pnl = np.array(pnls, dtype=float)
    trades = int(len(pnl))
    if trades == 0:
        return {"trades": 0, "winrate": 0.0, "profit_factor": 0.0, "max_dd": 0.0, "expectancy": 0.0, "net_pnl": 0.0}

    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    winrate = float(len(wins) / trades)
    profit_factor = float(wins.sum() / abs(losses.sum())) if len(losses) else 9999.0
    expectancy = float(pnl.mean())
    net = float(pnl.sum())

    equity = pnl.cumsum()
    peak = np.maximum.accumulate(equity)
    dd = equity - peak
    max_dd = float(dd.min())

    return {
        "trades": trades,
        "winrate": round(winrate, 4),
        "profit_factor": round(profit_factor, 4),
        "max_dd": round(max_dd, 4),
        "expectancy": round(expectancy, 6),
        "net_pnl": round(net, 4),
    }
