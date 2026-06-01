import pytest
import pandas as pd
import numpy as np
from app.core.indicators import add_indicators

def test_add_indicators():
    # Create dummy data
    data = {
        "high": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] * 20,
        "low": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] * 20,
        "close": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17] * 20,
        "volume": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100] * 20
    }
    df = pd.DataFrame(data)
    
    # Process indicators
    df_result = add_indicators(df)
    
    # Assertions
    assert "ema20" in df_result.columns
    assert "rsi14" in df_result.columns
    assert "atr" in df_result.columns
    assert "bb_high" in df_result.columns
    assert "supertrend" in df_result.columns
    assert len(df_result) == len(df)

