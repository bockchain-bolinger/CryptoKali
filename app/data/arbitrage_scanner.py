import asyncio
import ccxt.async_support as ccxt
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ArbitrageScanner:
    def __init__(self, symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT"]):
        self.symbols = symbols
        self.exchanges = {
            "binance": ccxt.binance({'enableRateLimit': True}),
            "kucoin": ccxt.kucoin({'enableRateLimit': True}),
            "bitget": ccxt.bitget({'enableRateLimit': True})
        }
        self.is_running = False
        self.latest_opportunities = []
        self.spreads_history = []
        
        # Simulierter State für "vom User abgelehnt -> ab ins Radar"
        self.rejected_opportunities = set()

    async def start_scanning(self):
        self.is_running = True
        logger.info(f"Starting Arbitrage Scanner on: {', '.join(self.exchanges.keys())}")
        
        while self.is_running:
            try:
                await self._scan_markets()
            except Exception as e:
                logger.error(f"Arbitrage Scanner error: {e}")
            await asyncio.sleep(10) # 10s Polling um Rate Limits zu schonen

    async def stop(self):
        self.is_running = False
        for ex in self.exchanges.values():
            await ex.close()

    async def _scan_markets(self):
        opportunities = []
        
        for symbol in self.symbols:
            tickers = {}
            for name, exchange in self.exchanges.items():
                try:
                    # fetch_ticker contains bid, ask, last
                    ticker = await exchange.fetch_ticker(symbol)
                    if ticker.get('bid') and ticker.get('ask'):
                        tickers[name] = ticker
                except Exception as e:
                    # Ignore temporary fetch errors per exchange
                    pass
            
            # Find best bid (highest price someone is willing to pay)
            # Find best ask (lowest price someone is willing to sell)
            if len(tickers) >= 2:
                best_bid_ex = max(tickers.keys(), key=lambda k: tickers[k]['bid'])
                best_ask_ex = min(tickers.keys(), key=lambda k: tickers[k]['ask'])
                
                best_bid = tickers[best_bid_ex]['bid']
                best_ask = tickers[best_ask_ex]['ask']
                
                # Spread in %
                # Profit if we buy at best_ask and sell at best_bid
                spread_pct = ((best_bid - best_ask) / best_ask) * 100
                
                # Assume 0.2% total fees (0.1% buy + 0.1% sell)
                if spread_pct > 0.2:
                    opp_id = f"{symbol}-{best_ask_ex}-{best_bid_ex}-{int(datetime.now().timestamp())}"
                    
                    opp = {
                        "id": opp_id,
                        "symbol": symbol,
                        "buy_exchange": best_ask_ex,
                        "buy_price": best_ask,
                        "sell_exchange": best_bid_ex,
                        "sell_price": best_bid,
                        "spread_pct": round(spread_pct, 4),
                        "timestamp": datetime.now().isoformat(),
                        "status": "pending_approval" # Wartet auf User Input
                    }
                    opportunities.append(opp)

        # Update lists (keep max 50 in history)
        if opportunities:
            self.latest_opportunities = sorted(opportunities, key=lambda x: x['spread_pct'], reverse=True)
            self.spreads_history.extend(opportunities)
            self.spreads_history = self.spreads_history[-50:]

    def get_latest_opportunities(self):
        return {
            "active": self.latest_opportunities,
            "history": self.spreads_history
        }

    def reject_opportunity(self, opp_id: str):
        self.rejected_opportunities.add(opp_id)
        for opp in self.latest_opportunities:
            if opp['id'] == opp_id:
                opp['status'] = "radar_only"

# Global Instance
arbitrage_scanner = ArbitrageScanner()
