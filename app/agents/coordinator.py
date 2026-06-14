"""
coordinator.py - Orchestrates all agents to produce a final trading recommendation.
"""
from app.agents.base_agent import BaseAgent
from app.agents.market_analyst import MarketAnalystAgent
from app.agents.risk_agent import RiskAgent
from app.agents.sentiment_agent import SentimentAgent
from app.agents.portfolio_agent import PortfolioAgent
from app.agents.strategies.trend_following_strategy import TrendFollowingStrategy
from app.agents.strategies.momentum_whale_strategy import MomentumWhaleStrategy
from app.data.whale_tracker import whale_tracker
from app.db import get_historical_win_rate
import requests
import os
import logging
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.market_analyst = MarketAnalystAgent()
        self.risk_agent = RiskAgent()
        self.sentiment_agent = SentimentAgent()
        self.portfolio_agent = PortfolioAgent()
        
        self.trend_strategy = TrendFollowingStrategy()
        self.whale_strategy = MomentumWhaleStrategy()

    @property
    def name(self): return "Coordinator"
    
    @property
    def description(self): return "Orchestrates agents for final recommendation"
    
    def analyze(self, context: dict) -> dict:
        symbol = context.get("symbol", "BTC/USDT")
        df = context.get("df")
        
        context["win_rate"] = get_historical_win_rate()
        
        # 1. Market Analyst
        market_res = self.market_analyst.analyze({"symbol": symbol, "df": df})
        
        # 2. Risk
        current_price = df['close'].iloc[-1] if (df is not None and not df.empty) else 0.0
        bias = market_res.get("bias", "neutral")
        
        if bias == "bullish":
            stop = current_price * 0.95
            tp1 = current_price * 1.10
        else:
            stop = current_price * 1.05
            tp1 = current_price * 0.90
            
        risk_res = self.risk_agent.analyze({
            "symbol": symbol,
            "entry": current_price,
            "stop": stop,
            "tp1": tp1,
            "score": market_res.get("confidence", 50),
            "open_positions": [],
            "equity": context.get("total_equity", 10000.0)
        })
        
        # 3. Sentiment
        sentiment_res = self.sentiment_agent.analyze({"symbol": symbol})
        
        # 4. Portfolio
        portfolio_res = self.portfolio_agent.analyze(context)
        
        # 3. Strategy Engine Evaluation
        strategy_context = {
            "market_bias": market_res.get("bias", "neutral"),
            "market_confidence": market_res.get("confidence", 0.0),
            "whale_data": whale_tracker.get_latest_data()
        }
        
        trend_eval = self.trend_strategy.analyze(symbol, df, strategy_context)
        whale_eval = self.whale_strategy.analyze(symbol, df, strategy_context)
        
        # 4. Final Recommendation Logic
        # Prioritize Whale Momentum if it's firing, otherwise fallback to Trend Following
        chosen_strategy = "None"
        recommendation = "WAIT"
        reason = "Marktbedingungen nicht eindeutig."
        
        if whale_eval["signal"] == "GO":
            recommendation = "GO"
            chosen_strategy = self.whale_strategy.name
            reason = whale_eval["reason"]
        elif trend_eval["signal"] == "GO":
            recommendation = "GO"
            chosen_strategy = self.trend_strategy.name
            reason = trend_eval["reason"]

        if risk_res.get("approved") is False:
            recommendation = "NO-GO"
            reason = f"Blockiert durch Risk Agent: {risk_res.get('reason')}"
            chosen_strategy = "None"
            
        # 5. LLM Swarm Validator (Second Opinion)
        if recommendation == "GO" and context.get("win_rate", 0) < 0.90:
            try:
                ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
                prompt = (
                    f"Du bist der Lead-Risk-Validator. Der Coordinator schlägt vor, {symbol} "
                    f"zu handeln basierend auf: {chosen_strategy}. \n"
                    f"Grund: {reason}\n"
                    f"CVD (Whale Data): {strategy_context['whale_data']['cvd'].get(symbol, 0)}\n"
                    f"Stimmst du diesem Trade zu? Antworte nur mit 'JA' oder 'NEIN' und einem kurzen Satz Begründung."
                )
                r = requests.post(ollama_url, json={
                    "model": os.getenv("OLLAMA_MODEL", "llama3"),
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }, timeout=10)
                if r.status_code == 200:
                    llm_answer = r.json().get("message", {}).get("content", "").upper()
                    if "NEIN" in llm_answer[:10]:
                        recommendation = "NO-GO"
                        reason = f"Veto durch LLM Swarm: {llm_answer}"
                        chosen_strategy = "None"
                    else:
                        reason += f" (LLM Swarm Approved)"
            except Exception as e:
                logging.error(f"LLM Swarm Validator failed: {e}")

        return {
            "symbol": symbol,
            "recommendation": recommendation,
            "chosen_strategy": chosen_strategy,
            "reason": reason,
            "size": risk_res.get("max_size_override", 0.0),
            "strategy_evals": {
                "trend": trend_eval,
                "whale": whale_eval
            },
            "agent_results": {
                "market_analyst": market_res,
                "sentiment": sentiment_res,
                "portfolio": portfolio_res,
                "risk": risk_res
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
