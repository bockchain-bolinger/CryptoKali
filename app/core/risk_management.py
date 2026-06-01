import pandas as pd
from app.config import settings

def calculate_position_size(equity: float, risk_pct: float, entry: float, stop: float) -> float:
    risk_amount = equity * risk_pct
    stop_dist = abs(entry - stop)
    if stop_dist == 0:
        return 0
    return risk_amount / stop_dist

def analyze_correlation(df_assets: pd.DataFrame) -> pd.DataFrame:
    # Basic correlation analysis of assets
    return df_assets.corr()
