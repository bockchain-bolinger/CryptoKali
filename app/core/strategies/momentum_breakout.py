from .base import Strategy
from app.core.regime import regime_gate
from app.core.risk import tps_from_r

class MomentumBreakoutStrategy(Strategy):
    def run(self, df):
        x = df.iloc[-1].to_dict()
        if not regime_gate(x, "trend"):
            return None
        if int(x["trend_up"]) != 1:
            return None
        if float(x.get("vol_impulse", 0)) < 1.6:
            return None
        if float(x.get("ret_24", 0)) < 0.03:
            return None
        rsi = float(x.get("rsi14", 50))
        if not (55 <= rsi <= 75):
            return None
        entry = float(x["swing_high_20"])
        stop = float(x["swing_low_20"])
        tp1, tp2 = tps_from_r(entry, stop, 2.0, 4.0, "long")
        return {"strategy":"momentum_breakout","direction":"long","entry":entry,"stop":stop,"tp1":tp1,"tp2":tp2,"tags":["momentum_breakout","trend_following"]}
