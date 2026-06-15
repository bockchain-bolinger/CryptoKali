import pandas as pd
import numpy as np
import logging
from typing import List, Dict
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import risk_matrix
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from app.db import connect

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    def __init__(self, db_connect_func=connect):
        self.connect = db_connect_func

    def get_historical_prices(self, symbols: List[str], timeframe: str = "1d", limit: int = 365) -> pd.DataFrame:
        """
        Fetches historical closing prices for multiple symbols and aligns them into a single DataFrame.
        """
        con = self.connect()
        price_data = {}
        
        for sym in symbols:
            query = """
                SELECT timestamp, close 
                FROM historical_ohlcv 
                WHERE symbol = %s AND timeframe = %s 
                ORDER BY timestamp DESC LIMIT %s
            """
            if type(con).__name__ != 'connection':
                query = query.replace("%s", "?")
                
            df = pd.read_sql_query(query, con, params=(sym, timeframe, limit))
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                # Sort back to ascending for correct returns calculation
                df.sort_index(inplace=True)
                price_data[sym] = df['close']
                
        con.close()
        
        if not price_data:
            return pd.DataFrame()
            
        prices_df = pd.DataFrame(price_data)
        prices_df.dropna(inplace=True) # Ensure we only use dates where all assets have data
        return prices_df

    def optimize_portfolio(self, symbols: List[str], total_portfolio_value: float = 10000.0) -> Dict:
        """
        Calculates the optimal portfolio weights (Max Sharpe) for the given symbols.
        Returns weights and discrete allocation if total_portfolio_value is provided.
        """
        if not symbols:
            return {"status": "error", "message": "No symbols provided."}
            
        prices = self.get_historical_prices(symbols, timeframe="1d", limit=365)
        
        if prices.empty or len(prices) < 30:
            return {"status": "error", "message": "Not enough historical daily data to optimize."}

        try:
            # 1. Calculate Expected Returns and Covariance Matrix
            # Krypto is traded 365 days a year
            mu = mean_historical_return(prices, frequency=365)
            S = risk_matrix(prices, method="sample_cov", frequency=365)

            # 2. Optimize for Maximum Sharpe Ratio
            ef = EfficientFrontier(mu, S, weight_bounds=(0.0, 1.0)) # Long only, max 100% per asset
            
            # We can also add constraints, e.g., max 50% in any single altcoin
            # ef.add_objective(objective_functions.L2_reg, gamma=0.1) 
            
            weights = ef.max_sharpe()
            cleaned_weights = ef.clean_weights()
            
            # Expected performance
            expected_annual_return, annual_volatility, sharpe_ratio = ef.portfolio_performance(verbose=False)
            
            # 3. Discrete Allocation (How many coins to buy)
            latest_prices = get_latest_prices(prices)
            da = DiscreteAllocation(cleaned_weights, latest_prices, total_portfolio_value=total_portfolio_value)
            allocation, leftover = da.lp_portfolio()
            
            return {
                "status": "success",
                "weights": dict(cleaned_weights),
                "allocation": allocation,
                "leftover_cash": round(leftover, 2),
                "performance": {
                    "expected_annual_return": round(expected_annual_return, 3),
                    "annual_volatility": round(annual_volatility, 3),
                    "sharpe_ratio": round(sharpe_ratio, 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            return {"status": "error", "message": str(e)}

portfolio_optimizer = PortfolioOptimizer()
