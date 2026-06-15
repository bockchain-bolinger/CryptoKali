import logging
import pandas as pd
import numpy as np
from app.db import get_historical_candles, save_backtest_result

# We can import our real indicators later to compute signals step-by-step
from app.core.indicators import calculate_all_indicators

logger = logging.getLogger(__name__)

class ApexAuditor:
    def __init__(self, initial_capital=10000.0, fee_rate=0.001, slippage=0.0005):
        self.initial_capital = initial_capital
        self.fee_rate = fee_rate
        self.slippage = slippage
        
        self.capital = initial_capital
        self.position = 0.0      # Current position size in asset
        self.entry_price = 0.0
        self.peak_capital = initial_capital
        
        self.trades = []
        self.equity_curve = []
        
    def reset(self):
        self.capital = self.initial_capital
        self.position = 0.0
        self.entry_price = 0.0
        self.peak_capital = self.initial_capital
        self.trades = []
        self.equity_curve = []

    def execute_trade(self, action: str, price: float, timestamp: int, size_pct: float = 0.5):
        """Simulate execution with fees and slippage."""
        if action == "BUY" and self.position == 0:
            # Entry
            exec_price = price * (1 + self.slippage)
            invest_amount = self.capital * size_pct
            fee = invest_amount * self.fee_rate
            
            self.capital -= (invest_amount + fee)
            self.position = invest_amount / exec_price
            self.entry_price = exec_price
            
        elif action == "SELL" and self.position > 0:
            # Exit
            exec_price = price * (1 - self.slippage)
            gross_return = self.position * exec_price
            fee = gross_return * self.fee_rate
            
            net_return = gross_return - fee
            pnl = net_return - (self.position * self.entry_price)
            pnl_pct = pnl / (self.position * self.entry_price) * 100
            
            self.capital += net_return
            
            self.trades.append({
                "entry_time": None, # Should track entry time ideally
                "exit_time": timestamp,
                "entry_price": self.entry_price,
                "exit_price": exec_price,
                "pnl": pnl,
                "pnl_pct": pnl_pct
            })
            
            self.position = 0.0
            self.entry_price = 0.0

    def calculate_metrics(self):
        total_trades = len(self.trades)
        if total_trades == 0:
            return {"trades": 0, "winrate": 0, "net_pnl": 0, "max_dd": 0, "profit_factor": 0, "expectancy": 0}
            
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        losing_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        winrate = len(winning_trades) / total_trades
        net_pnl = self.capital - self.initial_capital
        
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')
        
        # Max Drawdown
        equity_series = pd.Series([t['capital'] for t in self.equity_curve])
        if len(equity_series) > 0:
            running_max = equity_series.cummax()
            drawdowns = (equity_series - running_max) / running_max
            max_dd = abs(drawdowns.min()) * 100
        else:
            max_dd = 0.0
            
        # Expectancy
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['pnl_pct'] for t in losing_trades])) if losing_trades else 0
        expectancy = (winrate * avg_win) - ((1 - winrate) * avg_loss)
        
        return {
            "trades": total_trades,
            "winrate": winrate * 100,
            "net_pnl": net_pnl,
            "net_pnl_pct": (net_pnl / self.initial_capital) * 100,
            "max_dd": max_dd,
            "profit_factor": profit_factor,
            "expectancy": expectancy
        }

    def run_backtest(self, venue: str, symbol: str, timeframe: str, strategy: str = "MACD_Cross"):
        self.reset()
        
        # 1. Fetch data
        candles = get_historical_candles(venue.lower(), symbol, timeframe)
        if len(candles) < 50:
            logger.warning(f"Not enough data to backtest {symbol}. Found {len(candles)} candles.")
            return {"error": "Insufficient data"}
            
        # Convert to DataFrame for indicator calculation
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calculate indicators
        try:
            df = calculate_all_indicators(df)
        except Exception as e:
            logger.error(f"Error calculating indicators for backtest: {e}")
            return {"error": str(e)}
            
        # 2. Event Loop Simulation
        # Simple Example Strategy: MACD Crossover
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            timestamp = row['timestamp']
            price = row['close']
            
            # Record Equity Curve
            current_equity = self.capital + (self.position * price)
            self.equity_curve.append({"time": timestamp, "capital": current_equity})
            
            # --- STRATEGY LOGIC ---
            action = None
            if strategy == "MACD_Cross":
                # Buy when MACD crosses above Signal
                if prev_row.get('macd', 0) <= prev_row.get('macd_signal', 0) and row.get('macd', 0) > row.get('macd_signal', 0):
                    if row.get('rsi', 50) < 70: # Don't buy if overbought
                        action = "BUY"
                
                # Sell when MACD crosses below Signal
                elif prev_row.get('macd', 0) >= prev_row.get('macd_signal', 0) and row.get('macd', 0) < row.get('macd_signal', 0):
                    action = "SELL"
            else:
                # Add more strategies here later
                pass
                
            # Execute
            if action:
                self.execute_trade(action, price, timestamp)
                
        # Close out any remaining position at end of backtest
        if self.position > 0:
            self.execute_trade("SELL", df.iloc[-1]['close'], df.iloc[-1]['timestamp'])
            
        # 3. Finalize
        metrics = self.calculate_metrics()
        
        result_data = {
            "venue": venue,
            "symbol": symbol,
            "timeframe": timeframe,
            "strategy": strategy,
            "trades": metrics["trades"],
            "winrate": metrics["winrate"],
            "profit_factor": metrics["profit_factor"],
            "max_dd": metrics["max_dd"],
            "expectancy": metrics["expectancy"],
            "net_pnl": metrics["net_pnl"],
            "meta_json": {
                "equity_curve": self.equity_curve[::10], # Save every 10th point to save space
                "trades": self.trades
            }
        }
        
        # Save to DB
        bt_id = save_backtest_result(result_data)
        result_data["id"] = bt_id
        
        return result_data

auditor_engine = ApexAuditor()
