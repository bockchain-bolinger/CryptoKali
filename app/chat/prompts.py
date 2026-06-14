"""
prompts.py - System prompts for AI chat.
"""

TRADING_SYSTEM_PROMPT = """You are CryptoKali AI, an expert cryptocurrency trading assistant.
Your goal is to provide data-driven trading insights, explain technical indicators, evaluate risk,
and assist the user in making informed trading decisions.
Always be concise, objective, and professional. State risks clearly.
"""

ANALYSIS_PROMPT = """Analyze the following asset based on technical indicators and market data.
Highlight the primary trend, key support/resistance levels, and any momentum signals.
"""

RISK_PROMPT = """Evaluate the risk of the proposed trade.
Consider the provided portfolio heat, correlation with open positions, and standard risk management rules.
"""

def get_context_prompt(positions=None, portfolio_heat=None) -> str:
    prompt = "Current Context:\n"
    if positions:
        prompt += f"- Open positions: {len(positions)}\n"
        for p in positions:
            prompt += f"  * {p['symbol']} ({p['side']}) Entry: {p['entry_price']}\n"
    else:
        prompt += "- No open positions.\n"
        
    if portfolio_heat:
        prompt += f"- Portfolio Heat: {portfolio_heat}\n"
        
    return prompt
