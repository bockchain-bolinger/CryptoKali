from app.config import settings
from app.data.exchanges.binance import BinanceConnector
from app.core.risk_management import calculate_position_size
from app.db import save_order
from app.logger import logger

class OrderManager:
    def __init__(self):
        self.connector = BinanceConnector(is_futures=True)

    def place_order(self, symbol: str, side: str, entry_price: float, stop_price: float):
        # 1. Risk Check
        max_size = calculate_position_size(
            settings.ACCOUNT_EQUITY, 
            settings.RISK_PCT_PER_TRADE, 
            entry_price, 
            stop_price
        )
        
        # Simple guardrail
        if max_size <= 0:
            logger.error(f"Risk check failed for {symbol}: size <= 0")
            return None

        # 2. Place Order
        try:
            logger.info(f"Placing {side} order for {symbol} | Size: {max_size}")
            order = self.connector.exchange.create_order(
                symbol=symbol,
                type="limit",
                side=side,
                amount=max_size,
                price=entry_price,
                params={"timeInForce": "GTC"}
            )
            
            # 3. Save to DB
            save_order(
                venue="binance",
                symbol=symbol,
                order_id=order["id"],
                direction=side,
                price=entry_price,
                size=max_size,
                status=order["status"]
            )
            
            return order
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return None
