import logging
import json
import requests
from app.core.auditor import auditor_engine
from app.db import log_experiment_run

logger = logging.getLogger(__name__)

class ExperimentLab:
    def __init__(self, ollama_url="http://localhost:11434", default_model="llama3"):
        self.ollama_url = ollama_url
        self.default_model = default_model

    def run_experiment(self, name: str, venue: str, symbol: str, timeframe: str, strategy: str) -> dict:
        """
        Runs a backtest, generates an AI finding via Ollama, and logs the experiment.
        """
        logger.info(f"Starting Experiment Run: {name} ({strategy} on {symbol})")
        
        # 1. Run the Backtest
        result = auditor_engine.run_backtest(venue, symbol, timeframe, strategy)
        
        if "error" in result:
            logger.error(f"Experiment {name} failed: {result['error']}")
            return {"status": "error", "message": result["error"]}

        # Prepare metrics for AI
        metrics = {
            "trades": result["trades"],
            "winrate": result["winrate"],
            "profit_factor": result["profit_factor"],
            "max_dd": result["max_dd"],
            "net_pnl": result["net_pnl"]
        }

        # 2. Generate AI Finding via Ollama
        ai_finding = self._generate_ai_finding(name, symbol, strategy, metrics)

        # 3. Log to DB
        run_id = log_experiment_run(
            experiment_name=name,
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            metrics=metrics,
            ai_finding=ai_finding
        )

        logger.info(f"Experiment {name} completed and logged (ID: {run_id}).")
        
        return {
            "status": "success",
            "run_id": run_id,
            "metrics": metrics,
            "ai_finding": ai_finding
        }

    def _generate_ai_finding(self, name: str, symbol: str, strategy: str, metrics: dict) -> str:
        """Calls local Ollama API to interpret the backtest results."""
        prompt = f"""
Du bist ein quantitativer Krypto-Analyst. Analysiere diesen Backtest.
Experiment: {name}
Strategie: {strategy}
Symbol: {symbol}

Ergebnisse:
- Trades: {metrics['trades']}
- Winrate: {metrics['winrate']:.2f}%
- Profit Factor: {metrics['profit_factor']}
- Max Drawdown: {metrics['max_dd']:.2f}%
- Net PnL: ${metrics['net_pnl']:.2f}

Schreibe in 2-3 kurzen, prägnanten Sätzen eine professionelle Einschätzung auf Deutsch. 
Ist die Strategie bereit für den Live-Einsatz oder zu riskant?
"""
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.default_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30 # Wait up to 30s for the AI to generate
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.warning(f"Ollama API returned status {response.status_code}")
                return "AI-Analyse momentan nicht verfügbar (Ollama Error)."
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to connect to local Ollama API: {e}")
            return "AI-Analyse fehlgeschlagen. Ollama läuft möglicherweise nicht."

# Global Instance
lab = ExperimentLab()
