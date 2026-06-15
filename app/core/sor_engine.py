import asyncio
import ccxt.async_support as ccxt
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class SOREngine:
    def __init__(self):
        # Initialize exchange instances
        # We use a few popular ones with good liquidity
        self.exchanges = {
            "binance": ccxt.binance({'enableRateLimit': True}),
            "kucoin": ccxt.kucoin({'enableRateLimit': True}),
            "bitget": ccxt.bitget({'enableRateLimit': True})
        }

    async def close(self):
        """Clean up async exchange sessions."""
        for ex in self.exchanges.values():
            await ex.close()

    async def fetch_ticker_safe(self, exchange_id: str, symbol: str) -> dict:
        """Fetches ticker from a specific exchange safely."""
        exchange = self.exchanges[exchange_id]
        try:
            # Check if exchange has the symbol, or just try fetching
            ticker = await exchange.fetch_ticker(symbol)
            return {"exchange": exchange_id, "ticker": ticker, "status": "success"}
        except Exception as e:
            return {"exchange": exchange_id, "status": "error", "message": str(e)}

    async def get_best_execution(self, symbol: str, side: str, amount: float = 1.0) -> dict:
        """
        Smart Order Routing: Finds the best exchange to execute an order.
        side: 'buy' or 'sell'
        Returns the exchange with the lowest ask (for buy) or highest bid (for sell).
        """
        tasks = [self.fetch_ticker_safe(ex_id, symbol) for ex_id in self.exchanges.keys()]
        results = await asyncio.gather(*tasks)
        
        valid_results = [r for r in results if r["status"] == "success" and r["ticker"].get("ask") and r["ticker"].get("bid")]
        
        if not valid_results:
            return {"status": "error", "message": f"Could not fetch quotes for {symbol} on any exchange."}

        best_exchange = None
        best_price = float('inf') if side == 'buy' else 0.0
        
        quotes = []
        for r in valid_results:
            ex_id = r["exchange"]
            ask = r["ticker"]["ask"]
            bid = r["ticker"]["bid"]
            
            quotes.append({"exchange": ex_id, "bid": bid, "ask": ask})
            
            if side == 'buy':
                if ask < best_price:
                    best_price = ask
                    best_exchange = ex_id
            else: # sell
                if bid > best_price:
                    best_price = bid
                    best_exchange = ex_id
                    
        return {
            "status": "success",
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "best_exchange": best_exchange,
            "best_price": best_price,
            "estimated_value": best_price * amount,
            "quotes": quotes
        }

    async def scan_arbitrage(self, symbols: List[str] = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]) -> List[dict]:
        """
        Scans across multiple exchanges for spot arbitrage opportunities.
        Condition: Highest Bid (Exchange B) > Lowest Ask (Exchange A) + Fees
        """
        opportunities = []
        # Estimate average maker/taker fee across these exchanges is ~0.1% each side (0.2% total)
        FEE_ASSUMPTION = 0.002 
        
        for symbol in symbols:
            tasks = [self.fetch_ticker_safe(ex_id, symbol) for ex_id in self.exchanges.keys()]
            results = await asyncio.gather(*tasks)
            
            valid_results = [r for r in results if r["status"] == "success" and r["ticker"].get("ask") and r["ticker"].get("bid")]
            if len(valid_results) < 2:
                continue # Need at least 2 exchanges to compare
                
            # Find Lowest Ask (Where we Buy)
            lowest_ask = float('inf')
            buy_exchange = None
            
            # Find Highest Bid (Where we Sell)
            highest_bid = 0.0
            sell_exchange = None
            
            for r in valid_results:
                ask = r["ticker"]["ask"]
                bid = r["ticker"]["bid"]
                ex_id = r["exchange"]
                
                if ask < lowest_ask:
                    lowest_ask = ask
                    buy_exchange = ex_id
                    
                if bid > highest_bid:
                    highest_bid = bid
                    sell_exchange = ex_id
            
            if buy_exchange and sell_exchange and buy_exchange != sell_exchange:
                # Check Arbitrage Condition
                # We buy at lowest_ask and sell at highest_bid
                gross_spread_pct = (highest_bid - lowest_ask) / lowest_ask
                net_spread_pct = gross_spread_pct - FEE_ASSUMPTION
                
                # Even if negative, we report the best spread to populate the UI (just for visual representation)
                opportunities.append({
                    "symbol": symbol,
                    "buy_exchange": buy_exchange,
                    "buy_price": lowest_ask,
                    "sell_exchange": sell_exchange,
                    "sell_price": highest_bid,
                    "gross_spread_pct": round(gross_spread_pct * 100, 4),
                    "net_spread_pct": round(net_spread_pct * 100, 4),
                    "is_profitable": net_spread_pct > 0
                })
                
        # Sort by best net spread
        opportunities.sort(key=lambda x: x["net_spread_pct"], reverse=True)
        return opportunities

sor_engine = SOREngine()
