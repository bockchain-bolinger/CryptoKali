"""
handler.py - Processes incoming chat messages.
"""
import os
import logging
import requests
from app.chat.history import ChatHistory
from app.chat.prompts import TRADING_SYSTEM_PROMPT, get_context_prompt
from app.db import get_paper_trades

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.history = ChatHistory()
        self.use_openai = bool(os.getenv("OPENAI_API_KEY"))
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3") # standard fallback
        
        if self.use_openai:
            import openai
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            self.client = None

    def process_message(self, session_id: str, message: str, context: dict = None) -> dict:
        if context is None:
            context = {}
        self.history.add_message(session_id, "user", message)
        
        command, args = self.parse_slash_command(message)
        response_text = ""
        data = {}
        agent_used = "RuleBased"

        if command:
            if command == "analyze":
                symbol = args[0] if args else "BTC/USDT"
                response_text = f"Executing analysis for {symbol}...\n(In a real setup, CoordinatorAgent would run here.)"
                data = {"symbol": symbol, "action": "analyze"}
                agent_used = "Coordinator"
            elif command == "signals":
                response_text = "Fetching latest trading signals...\n(Mock data: Long BTC, Short ETH)"
                data = {"action": "signals"}
            elif command == "portfolio":
                response_text = "Fetching portfolio overview...\n(Mock data: 2 open positions, low risk)"
                data = {"action": "portfolio"}
            elif command == "risk":
                response_text = "Evaluating portfolio risk...\n(Mock data: Risk is within limits)"
                data = {"action": "risk"}
            elif command == "explain":
                trade_id = args[0] if args else None
                if not trade_id:
                    response_text = "Bitte gib eine Trade ID an: /explain 1"
                else:
                    trades = get_paper_trades()
                    trade = next((t for t in trades if str(t['id']) == str(trade_id)), None)
                    if not trade:
                        response_text = f"Trade {trade_id} nicht gefunden."
                    else:
                        response_text = f"Erkläre Trade {trade_id}...\n(In einem echten Setup würde die KI hier die Makro-Daten von diesem Zeitpunkt analysieren. Trade: {trade['side']} {trade['symbol']} @ {trade['entry_price']})"
                        # Hier würde der Post-Mortem Prompt an Ollama gehen
                data = {"action": "explain", "trade_id": trade_id}
            elif command == "help":
                response_text = "Available commands:\n/analyze SYMBOL\n/signals\n/portfolio\n/risk\n/explain TRADE_ID\n/help"
            else:
                response_text = f"Unknown command: {command}. Type /help for a list of commands."
        else:
            messages = [{"role": "system", "content": "Du bist ein professioneller Krypto- und Makroökonomie-Mentor. Erkläre Konzepte einfach und verständlich."}]
            ctx_prompt = get_context_prompt(context.get("positions"), context.get("portfolio_heat"))
            messages.append({"role": "system", "content": ctx_prompt})
            
            hist = self.history.get_history(session_id, last_n=10)
            messages.extend(hist)

            if self.use_openai:
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=0.7
                    )
                    response_text = response.choices[0].message.content
                    agent_used = "OpenAI"
                except Exception as e:
                    logger.error(f"OpenAI error: {e}")
                    response_text = "Sorry, I encountered an error communicating with OpenAI."
            else:
                # OLLAMA FALLBACK
                try:
                    ollama_payload = {
                        "model": self.ollama_model,
                        "messages": messages,
                        "stream": False
                    }
                    r = requests.post(self.ollama_url, json=ollama_payload, timeout=30)
                    if r.status_code == 200:
                        response_text = r.json().get("message", {}).get("content", "")
                        agent_used = f"Ollama ({self.ollama_model})"
                    else:
                        response_text = "Ich bin aktuell im Offline-Modus und Ollama ist nicht erreichbar. Bitte starte deinen lokalen Ollama Server."
                        agent_used = "RuleBased"
                except Exception as e:
                    logger.error(f"Ollama error: {e}")
                    response_text = "Ollama ist nicht erreichbar. Hast du `ollama serve` im Terminal gestartet?"
                    agent_used = "RuleBased"

        self.history.add_message(session_id, "assistant", response_text)
        
        return {
            "response_text": response_text,
            "data": data,
            "agent_used": agent_used
        }

    def parse_slash_command(self, message: str):
        message = message.strip()
        if message.startswith("/"):
            parts = message.split()
            command = parts[0][1:].lower()
            args = parts[1:]
            return command, args
        return None, None
