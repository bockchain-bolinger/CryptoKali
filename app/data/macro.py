import yfinance as yf
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def get_macro_data() -> dict:
    """
    Fetches macroeconomic data via yfinance (free, no API key).
    DXY: US Dollar Index (Inverse correlation to Crypto)
    IRX: 13-Week Treasury Bill (Proxy for US Interest Rates)
    """
    try:
        # Fetch DXY
        dxy_ticker = yf.Ticker("DX-Y.NYB")
        dxy_data = dxy_ticker.history(period="5d")
        if not dxy_data.empty:
            dxy_close = float(dxy_data['Close'].iloc[-1])
            dxy_prev = float(dxy_data['Close'].iloc[-2]) if len(dxy_data) > 1 else dxy_close
            dxy_change = ((dxy_close - dxy_prev) / dxy_prev) * 100
        else:
            dxy_close, dxy_change = 104.5, 0.0

        # Fetch 13-Week T-Bill Yield (Interest Rate Proxy)
        irx_ticker = yf.Ticker("^IRX")
        irx_data = irx_ticker.history(period="5d")
        if not irx_data.empty:
            irx_close = float(irx_data['Close'].iloc[-1])
            irx_prev = float(irx_data['Close'].iloc[-2]) if len(irx_data) > 1 else irx_close
            irx_change = ((irx_close - irx_prev) / irx_prev) * 100
        else:
            irx_close, irx_change = 5.25, 0.0

        # Analyze Macro Environment for Crypto
        # Weak DXY & Dropping Yields = High Global Liquidity -> Bullish for Crypto
        status = "Neutral"
        if dxy_change < -0.2 and irx_change < -0.5:
            status = "Strong Bullish (High Liquidity)"
        elif dxy_change < 0 and irx_change <= 0:
            status = "Bullish"
        elif dxy_change > 0.2 and irx_change > 0.5:
            status = "Strong Bearish (Liquidity Drain)"
        elif dxy_change > 0 or irx_change > 0:
            status = "Bearish"

        return {
            "dxy": {"value": round(dxy_close, 2), "change_pct": round(dxy_change, 2)},
            "interest_rates": {"value": round(irx_close, 2), "change_pct": round(irx_change, 2)},
            "crypto_impact": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to fetch macro data: {e}")
        return {
            "dxy": {"value": 104.5, "change_pct": 0.0},
            "interest_rates": {"value": 5.25, "change_pct": 0.0},
            "crypto_impact": "Unknown",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
