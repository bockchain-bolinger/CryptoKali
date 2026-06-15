import logging
import os
from openai import AsyncOpenAI
from app.data.macro import get_macro_data

logger = logging.getLogger(__name__)

class MacroAgent:
    """
    MacroAgent: Specializes in predicting crypto market movements based on macro-economic shifts.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None

    async def simulate_scenario(self, dxy_change_pct: float, rate_change_pct: float) -> dict:
        """
        Simulates the effect of DXY and Interest Rate changes on BTC, ETH, and general market.
        Uses historical beta (negative correlation to DXY and rates) to estimate price impact,
        and generates an LLM summary.
        """
        # Baseline historical betas (simplified approximations):
        # - A 1% drop in DXY historically correlates with a ~3-5% rise in BTC.
        # - A 1% drop in FED Rates correlates with a ~10-15% rise in BTC over mid-term.
        btc_impact_pct = (dxy_change_pct * -4.0) + (rate_change_pct * -12.0)
        eth_impact_pct = btc_impact_pct * 1.25 # ETH usually has higher beta
        tvl_impact_pct = (rate_change_pct * -15.0) # TVL explodes when rates drop (yield farming becomes attractive vs T-Bills)
        
        # Current data mock or real (fetch actual if needed, here we use baseline assumptions for UI)
        current_btc = 65000.0
        current_eth = 3500.0
        
        projected_btc = current_btc * (1 + (btc_impact_pct / 100))
        projected_eth = current_eth * (1 + (eth_impact_pct / 100))
        
        sentiment_label = "Extremely Bullish" if btc_impact_pct > 15 else "Bullish" if btc_impact_pct > 0 else "Neutral" if btc_impact_pct == 0 else "Bearish" if btc_impact_pct > -15 else "Extremely Bearish"
        
        report = ""
        if self.client:
            prompt = f"""
You are the Apex AI Macro-Economist. The user has simulated a macroeconomic scenario:
- DXY (US Dollar Index) change: {dxy_change_pct}%
- Interest Rates change: {rate_change_pct}%

The mathematical projection indicates a {btc_impact_pct:.1f}% impact on Bitcoin.
Write a very brief, punchy "Flash Report" (max 3 sentences) explaining WHY the market will react this way to these specific macro changes.
Use professional institutional terminology (e.g., liquidity, flight to safety, risk-on, cost of capital).
"""
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=150,
                    temperature=0.4
                )
                report = response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Macro Agent LLM Error: {e}")
                report = self._generate_fallback_report(dxy_change_pct, rate_change_pct, btc_impact_pct)
        else:
            report = self._generate_fallback_report(dxy_change_pct, rate_change_pct, btc_impact_pct)

        return {
            "status": "success",
            "scenario": {
                "dxy_change_pct": dxy_change_pct,
                "rate_change_pct": rate_change_pct
            },
            "projections": {
                "btc_impact_pct": round(btc_impact_pct, 2),
                "eth_impact_pct": round(eth_impact_pct, 2),
                "tvl_impact_pct": round(tvl_impact_pct, 2),
                "projected_btc": round(projected_btc, 2),
                "projected_eth": round(projected_eth, 2),
                "sentiment": sentiment_label
            },
            "report": report
        }

    def _generate_fallback_report(self, dxy_change, rate_change, btc_impact):
        if btc_impact > 0:
            return f"A decrease in the US Dollar (DXY by {dxy_change}%) and easing monetary policy (Rates by {rate_change}%) reduces the cost of capital. Capital flows aggressively into risk-on assets like crypto seeking higher yields."
        elif btc_impact < 0:
            return f"A strengthening dollar (DXY by {dxy_change}%) and tightening liquidity (Rates by {rate_change}%) triggers a flight to safety. Risk-on assets like crypto suffer heavy outflows as investors lock in risk-free yields."
        else:
            return "Macro conditions remain balanced, suggesting sideways consolidation for risk assets."

macro_agent = MacroAgent()
