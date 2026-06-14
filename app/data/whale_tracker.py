import asyncio
import websockets
import json
import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class WhaleTracker:
    def __init__(self, min_whale_size_usdt: float = 50000.0):
        self.min_whale_size = min_whale_size_usdt
        self.whale_alerts = deque(maxlen=20)
        
        # CVD = Cumulative Volume Delta (Buy Vol - Sell Vol)
        self.cvd = {"BTC/USDT": 0.0, "ETH/USDT": 0.0}
        
        self.symbols_map = {
            "btcusdt": "BTC/USDT",
            "ethusdt": "ETH/USDT"
        }
        self.is_running = False

    async def start_tracking(self):
        self.is_running = True
        uri = "wss://stream.binance.com:9443/ws/btcusdt@aggTrade/ethusdt@aggTrade"
        
        while self.is_running:
            try:
                logger.info(f"Connecting to Binance Whale Stream... (Min Size: {self.min_whale_size} USDT)")
                async with websockets.connect(uri) as websocket:
                    while self.is_running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        self._process_trade(data)
            except Exception as e:
                if self.is_running:
                    logger.error(f"WhaleTracker WebSocket disconnected: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)

    def stop(self):
        self.is_running = False

    def _process_trade(self, data: dict):
        try:
            symbol_raw = data.get("s", "").lower()
            symbol = self.symbols_map.get(symbol_raw)
            if not symbol:
                return

            price = float(data.get("p", 0))
            quantity = float(data.get("q", 0))
            is_buyer_maker = data.get("m", True)  # If buyer is maker, it's a SELL trade. If false, it's a BUY trade.
            
            trade_value = price * quantity
            side = "SELL" if is_buyer_maker else "BUY"
            
            # Update CVD
            delta = trade_value if side == "BUY" else -trade_value
            self.cvd[symbol] += delta
            
            # Check for Whale
            if trade_value >= self.min_whale_size:
                alert = {
                    "id": data.get("a", 0),
                    "symbol": symbol,
                    "side": side,
                    "price": price,
                    "value_usdt": round(trade_value, 2),
                    "timestamp": datetime.now().isoformat()
                }
                self.whale_alerts.appendleft(alert)
                
        except Exception as e:
            pass 

    def get_latest_data(self):
        return {
            "cvd": {
                "BTC/USDT": round(self.cvd.get("BTC/USDT", 0), 2),
                "ETH/USDT": round(self.cvd.get("ETH/USDT", 0), 2)
            },
            "recent_whales": list(self.whale_alerts)
        }

# Global instance
whale_tracker = WhaleTracker()
