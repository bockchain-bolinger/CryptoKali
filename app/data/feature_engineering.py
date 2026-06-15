import pandas as pd
import numpy as np
import ta
import logging
from app.db import connect

logger = logging.getLogger(__name__)

def load_ohlcv_from_db(symbol: str, timeframe: str = "1h", limit: int = 5000) -> pd.DataFrame:
    """Loads historical data from DB into a DataFrame."""
    con = connect()
    query = """
        SELECT timestamp, open, high, low, close, volume 
        FROM historical_ohlcv 
        WHERE symbol = %s AND timeframe = %s 
        ORDER BY timestamp ASC LIMIT %s
    """
    
    # SQLite fallback
    if type(con).__name__ != 'connection':
        query = query.replace("%s", "?")
        
    df = pd.read_sql_query(query, con, params=(symbol, timeframe, limit))
    con.close()
    
    if df.empty:
        return df
        
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def generate_features(df: pd.DataFrame, target_periods: int = 4) -> pd.DataFrame:
    """
    Generates ML features and the target label.
    target_periods: How many periods ahead to look for the target label.
    """
    if df.empty or len(df) < 50:
        return df
        
    data = df.copy()
    
    # 1. Price Returns
    data['ret_1'] = data['close'].pct_change(1)
    data['ret_3'] = data['close'].pct_change(3)
    data['ret_5'] = data['close'].pct_change(5)
    
    # 2. Volatility (Rolling Std Dev of returns)
    data['volatility_5'] = data['ret_1'].rolling(window=5).std()
    data['volatility_15'] = data['ret_1'].rolling(window=15).std()
    
    # 3. Technical Indicators (Normalized where possible)
    # RSI
    data['rsi'] = ta.momentum.RSIIndicator(close=data['close'], window=14).rsi()
    
    # MACD Histogram
    macd = ta.trend.MACD(close=data['close'])
    data['macd_diff'] = macd.macd_diff()
    
    # Bollinger Bands (%B)
    bb = ta.volatility.BollingerBands(close=data['close'], window=20, window_dev=2)
    data['bb_pband'] = bb.bollinger_pband()
    
    # ATR (Normalized by close price)
    atr = ta.volatility.AverageTrueRange(high=data['high'], low=data['low'], close=data['close'], window=14)
    data['atr_norm'] = atr.average_true_range() / data['close']
    
    # 4. Target Label Generation
    # We want to predict if the price will be higher in `target_periods` steps.
    data['future_return'] = data['close'].pct_change(target_periods).shift(-target_periods)
    
    # Label: 1 if future_return > 0 (Bullish), 0 if <= 0 (Bearish/Flat)
    data['target'] = (data['future_return'] > 0.0).astype(int)
    
    # Drop rows with NaN (due to rolling windows and shifts)
    # Exclude the 'future_return' from features
    data.dropna(inplace=True)
    
    return data

def get_latest_features(symbol: str, timeframe: str = "1h") -> dict:
    """Gets the very last row of features for live prediction."""
    df = load_ohlcv_from_db(symbol, timeframe, limit=100)
    if df.empty:
        return {}
        
    data = generate_features(df, target_periods=1) # Target periods doesn't matter for the last row
    
    if data.empty:
        return {}
        
    # We drop 'target' and 'future_return' because they might be NaN or irrelevant for prediction
    latest = data.iloc[-1].drop(['target', 'future_return'], errors='ignore')
    return latest.to_dict()
