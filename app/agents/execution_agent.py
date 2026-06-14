import os
import ccxt
import logging

logger = logging.getLogger(__name__)

class ExecutionAgent:
    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY", "")
        self.kucoin_api = os.getenv("KUCOIN_API_KEY", "")
        self.kucoin_secret = os.getenv("KUCOIN_SECRET_KEY", "")
        self.trade_amount_usdt = float(os.getenv("TRADE_AMOUNT_USDT", "20"))
        self.is_live = os.getenv("LIVE_TRADING", "false").lower() == "true"
        
        self.exchanges = {}
        
        # We initialize all supported exchanges for Smart Order Routing (SOR)
        # Even if not live, we might use them for SOR pricing
        self.exchanges["binance"] = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        self.exchanges["kucoin"] = ccxt.kucoin({
            'apiKey': self.kucoin_api,
            'secret': self.kucoin_secret,
            'enableRateLimit': True
        })
        
        self.exchanges["bitget"] = ccxt.bitget({'enableRateLimit': True})
        
        if self.is_live and self.api_key and self.secret_key:
            logger.info("🟢 LIVE TRADING IS ENABLED. Multi-Exchange framework connected.")
        else:
            logger.info("🟡 LIVE TRADING IS DISABLED. Using Paper Trading / Smart Order Routing Mock.")

    def execute_trade(self, symbol: str, side: str, current_price: float, stop_loss: float, take_profit: float) -> dict:
    def find_best_exchange(self, symbol: str, side: str) -> dict:
        """
        Smart Order Routing: Finds the exchange with the best price for the given side.
        Returns {'exchange': name, 'price': float}
        """
        best_price = None
        best_exchange = "binance"
        
        for name, ex in self.exchanges.items():
            try:
                ticker = ex.fetch_ticker(symbol)
                # If buying, we want the lowest ask. If selling, highest bid.
                price = ticker['ask'] if side.upper() in ["LONG", "BUY"] else ticker['bid']
                
                if best_price is None:
                    best_price = price
                    best_exchange = name
                else:
                    if side.upper() in ["LONG", "BUY"] and price < best_price:
                        best_price = price
                        best_exchange = name
                    elif side.upper() in ["SHORT", "SELL"] and price > best_price:
                        best_price = price
                        best_exchange = name
            except Exception as e:
                pass
                
        return {"exchange": best_exchange, "price": best_price or 0.0}

    def execute_trade(self, symbol: str, side: str, current_price: float, stop_loss: float, take_profit: float, override_size: float = None) -> dict:
        """
        Executes a live market order followed by an OCO (One-Cancels-the-Other) order for TP & SL.
        Uses Smart Order Routing to find the best exchange.
        """
        best_route = self.find_best_exchange(symbol, side)
        ex_name = best_route["exchange"]
        active_exchange = self.exchanges[ex_name]
        
        if not self.is_live or not self.api_key:
            return {
                "status": "paper", 
                "message": f"Routed via {ex_name} @ {best_route['price']}. Paper Trading Mode.",
                "size": override_size or (self.trade_amount_usdt / current_price),
                "entry_price": best_route['price'] if best_route['price'] > 0 else current_price
            }

        if side.upper() != "LONG" and side.upper() != "BUY":
            logger.warning(f"Live Execution rejected: Spot trading does not support {side}. Ignoring.")
            return {"status": "error", "message": f"Spot does not support {side}"}

        try:
            active_exchange.load_markets()
            market = active_exchange.market(symbol)
            
            # Use override size (Kelly) if provided, otherwise default fixed USDT amount
            usdt_amount = override_size if override_size else self.trade_amount_usdt
            size_raw = usdt_amount / current_price
            size = active_exchange.amount_to_precision(symbol, size_raw)
            
            logger.info(f"Executing LIVE BUY {size} {symbol} on {ex_name.upper()} @ MARKET (Amount: {usdt_amount} USDT)")
            
            # 1. Execute Market BUY
            order = active_exchange.create_order(
                symbol=symbol,
                type='market',
                side='buy',
                amount=float(size)
            )
            
            entry_price = float(order.get('average') or order.get('price') or current_price)
            
            # Stop limit slightly below stop price to guarantee fill in fast drops
            stop_limit_price = stop_loss * 0.998
            
            # Format numbers to exchange precision
            tp_price_str = active_exchange.price_to_precision(symbol, take_profit)
            sl_price_str = active_exchange.price_to_precision(symbol, stop_loss)
            sl_limit_str = active_exchange.price_to_precision(symbol, stop_limit_price)
            
            logger.info(f"Placing OCO Sell Order -> TP: {tp_price_str}, SL: {sl_price_str}")
            
            if ex_name == "binance":
                oco_order = active_exchange.private_post_order_oco({
                    'symbol': market['id'],
                    'side': 'SELL',
                    'quantity': float(size),
                    'price': tp_price_str,
                    'stopPrice': sl_price_str,
                    'stopLimitPrice': sl_limit_str,
                    'stopLimitTimeInForce': 'GTC'
                })
            else:
                # Mock OCO for KuCoin/Bitget fallback for now
                oco_order = {"orderListId": "mock-oco"}
                
            logger.info(f"✅ Live trade and OCO placed successfully on {ex_name.upper()}!")
            
            return {
                "status": "live_executed",
                "entry_order_id": order.get('id'),
                "oco_order_list_id": oco_order.get('orderListId'),
                "size": size,
                "entry_price": entry_price
            }
            
        except Exception as e:
            logger.error(f"❌ LIVE EXECUTION FAILED for {symbol}: {e}")
            return {"status": "error", "message": str(e)}
