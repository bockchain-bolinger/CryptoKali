import logging
import os
from openai import AsyncOpenAI
from app.db import save_trade_lesson

logger = logging.getLogger(__name__)

class EvolutionAgent:
    """
    Apex Evolution: Continuous Learning Agent.
    Analyzes closed trades to extract 'Lessons Learned' and saves them to the DB.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            
    async def run_post_mortem(self, trade_id: int, symbol: str, entry_price: float, exit_price: float, side: str, pnl: float) -> str:
        """
        Triggers after a trade is closed. Analyzes why it won/lost.
        """
        logger.info(f"Evolution Agent started Post-Mortem for Trade {trade_id} ({symbol}). PnL: {pnl}")
        
        market_context = f"Trade: {side} {symbol} | Entry: {entry_price} | Exit: {exit_price} | PnL: {pnl}"
        
        prompt = f"""
You are the "Apex Evolution" agent, the continuous learning core of an institutional crypto AI.
A trade has just been closed. Your job is to analyze the outcome and write a concise "Lesson Learned" (max 3 sentences).
If the trade was profitable, explain what likely went right. If it was a loss, explain what likely went wrong.

Trade Details:
- Symbol: {symbol}
- Side: {side.upper()}
- Entry Price: ${entry_price:.2f}
- Exit Price: ${exit_price:.2f}
- P&L: ${pnl:.2f}

Format your response as a direct, actionable lesson. Be analytical, professional, and do not use generic filler words.
"""

        lesson = ""
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=150,
                    temperature=0.4
                )
                lesson = response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Evolution Agent LLM Error: {e}")
                lesson = f"Trade resulted in {'Profit' if pnl > 0 else 'Loss'}. Market conditions shifted after entry."
        else:
            # Fallback if no LLM configured
            lesson = "Successful momentum capture." if pnl > 0 else "Trade reversed against entry bias. Consider tighter stops or checking higher timeframe."
            
        logger.info(f"Evolution Lesson Learned: {lesson}")
        
        # Save to DB
        save_trade_lesson(trade_id, symbol, pnl, market_context, lesson)
        
        return lesson

evolution_agent = EvolutionAgent()
