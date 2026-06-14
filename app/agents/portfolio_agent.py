"""
portfolio_agent.py - Analyzes current portfolio risk and correlation.
"""
from app.agents.base_agent import BaseAgent
from app.db import connect
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class PortfolioAgent(BaseAgent):
    @property
    def name(self): return "PortfolioAgent"
    
    @property
    def description(self): return "Analyzes portfolio positions, risk and correlation"
    
    def analyze(self, context: dict) -> dict:
        try:
            conn = connect()
            c = conn.cursor()
            c.execute("SELECT id, symbol, side, entry_price, size, stop FROM paper_trades WHERE status='open'")
            rows = c.fetchall()
            conn.close()
        except Exception as e:
            logger.error("DB error in PortfolioAgent: %s", e)
            rows = []
            
        positions = []
        longs = 0
        shorts = 0
        total_risk_usd = 0.0
        
        for row in rows:
            pos = {
                "id": row[0],
                "symbol": row[1],
                "side": row[2],
                "entry_price": row[3],
                "size": row[4],
                "stop": row[5]
            }
            positions.append(pos)
            if pos["side"].lower() == "buy":
                longs += 1
            else:
                shorts += 1
                
            if pos["entry_price"] and pos["stop"] and pos["size"]:
                risk_per_unit = abs(pos["entry_price"] - pos["stop"])
                risk_usd = risk_per_unit * pos["size"]
                total_risk_usd += risk_usd
                
        total_equity = context.get("total_equity", 10000.0)
        total_risk_pct = (total_risk_usd / total_equity) * 100 if total_equity > 0 else 0
        
        heat_level = "low"
        if total_risk_pct > 5.0:
            heat_level = "high"
        elif total_risk_pct > 2.0:
            heat_level = "medium"
            
        correlation_warning = False
        if (longs > 3 and shorts == 0) or (shorts > 3 and longs == 0):
            correlation_warning = True
            
        return {
            "agent": self.name,
            "total_risk_pct": round(total_risk_pct, 2),
            "positions_count": len(positions),
            "heat_level": heat_level,
            "correlation_warning": correlation_warning,
            "positions": positions,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
