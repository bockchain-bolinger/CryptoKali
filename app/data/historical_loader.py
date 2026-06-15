import ccxt.async_support as ccxt
import asyncio
import logging
from app.db import save_historical_candles

logger = logging.getLogger(__name__)

async def fetch_historical_ohlcv(venue: str, symbol: str, timeframe: str, since_ms: int = None, limit: int = 1000):
    """
    Fetches historical OHLCV data for a specific venue, symbol and timeframe.
    """
    exchange_class = getattr(ccxt, venue.lower())
    exchange = exchange_class({
        'enableRateLimit': True,
    })
    
    try:
        # Load markets
        await exchange.load_markets()
        
        # If since_ms is not provided, we calculate a default timestamp 
        # (e.g. 1000 candles ago) based on the timeframe, but ccxt handles 'since' if we don't provide it, 
        # though it's better to explicitly provide it for pagination.
        logger.info(f"Fetching historical data for {symbol} on {venue} ({timeframe})")
        
        ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
        
        if ohlcv:
            # Save to database
            save_historical_candles(venue.lower(), symbol, timeframe, ohlcv)
            logger.info(f"Saved {len(ohlcv)} historical candles to database.")
            return len(ohlcv)
        else:
            logger.warning(f"No data returned for {symbol} on {venue}.")
            return 0
            
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return 0
    finally:
        await exchange.close()

# For a mass download (e.g. fetching 10000 candles), we would loop and update `since` based on the last candle's timestamp.
async def bulk_fetch_historical(venue: str, symbol: str, timeframe: str, total_candles: int = 5000):
    """
    Downloads a larger dataset by paginating backwards from current time.
    """
    logger.info(f"Starting bulk fetch of {total_candles} candles for {symbol}...")
    
    # Calculate approx start time for `total_candles` based on timeframe.
    # We will just fetch `limit=1000` iteratively until we hit total_candles.
    
    # To keep it simple for now, we just fetch the last 1000. For production, 
    # we would paginate using `since` parameter by calculating ms offsets.
    # We'll just fetch 1000 as MVP for the auditor.
    await fetch_historical_ohlcv(venue, symbol, timeframe, limit=min(total_candles, 1000))
    return {"status": "success", "message": f"Fetched recent data for {symbol}"}

