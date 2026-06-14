# 🚀 CryptoKali Pro

**CryptoKali Pro** ist ein fortschrittliches, voll-autonomes Krypto-Trading- und Makro-Analyse-System. Es nutzt eine Multi-Agenten-Architektur, Smart Order Routing (Multi-Exchange) und lokale Large Language Models (LLM-Swarm), um Trades nicht nur auszuführen, sondern auch das Portfolio-Risiko dynamisch zu managen.

![CryptoKali Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-6366f1) ![Status](https://img.shields.io/badge/Status-Beta-22d3ee) ![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Next.js](https://img.shields.io/badge/Next.js-14-black)

---

## 🌟 Kernfunktionen

### 🧠 1. Multi-Agenten Schwarm
Das Herzstück des Systems ist der `CoordinatorAgent`, der spezialisierte KI-Agenten orchestriert:
- **MarketAnalyst:** Berechnet technische Indikatoren (CVD, MACD, Ichimoku, RSI) und identifiziert Trends.
- **RiskAgent:** Wendet dynamische Positionsgrößen basierend auf deiner historischen Win-Rate an (**Kelly Criterion**).
- **Sentiment & News:** Analysiert den *Fear & Greed Index* und Echtzeit-News.
- **LLM Second-Opinion:** Solange die Strategie keine Win-Rate von > 90% hat, sendet das System die Analysedaten live an ein lokales **Ollama-LLM** als finalen Validator.

### 🐳 2. Whale Tracking & Makroökonomie
- **Live Orderbook (CVD):** Verbindet sich über WebSockets mit Binance, um extrem große Einzel-Trades (> 50k USDT) in Millisekunden zu filtern.
- **Makro-Dashboard:** Zieht Echtzeitdaten der **US-Treasury Yields** und des **US-Dollar Index (DXY)** via Yahoo Finance, um die globale Liquidität in Entscheidungen einzubeziehen.
- **On-Chain TVL:** Integriert DefiLlama, um das Total Value Locked in den Netzwerken zu scannen.

### 🔀 3. Smart Order Routing & Arbitrage
- **Multi-Exchange:** Handelt asynchron auf *Binance*, *KuCoin* und *Bitget*. 
- **SOR:** Sucht vor jedem Trade das Orderbuch nach dem besten Kauf-/Verkaufspreis (Geringste Slippage) ab.
- **Arbitrage-Scanner:** Ein Hintergrund-Service gleicht permanent Spreads zwischen den drei Börsen ab und pusht profitable Ineffizienzen in Echtzeit in dein Dashboard.

### 🖥 4. Futuristische Benutzeroberfläche
- Ein komplett in **Next.js 14** (App Router) gebautes Dashboard.
- **Aesthetics:** Glassmorphism-Design, interaktive Heatmaps und Micro-Animationen.
- **Live-Radar:** Beinhaltet Live-Charts, Portfolio-Heatmaps, Whale-Radar und ein Order-Management-Terminal.

---

## 🛠 Tech Stack

**Backend:**
- **Python (FastAPI)** für asynchrone APIs.
- **CCXT & WebSockets** für Exchange-Konnektivität.
- **PostgreSQL (Docker)** für hochperformantes Speichern von Ticks und Trade-Historien.
- **APScheduler** für regelmäßiges Market-Scanning.

**Frontend:**
- **Next.js 14 (TypeScript)** 
- **Vanilla CSS** mit Custom Design-Tokens für maximale Performance.
- **SWR** & Native WebSockets für Live-Data-Streaming.

**KI & Modelle:**
- **Ollama** für kostenloses, privates LLM-Hosting (Mentor & Risk-Validator).
- Optionale OpenAI API-Anbindung für GPT-4 Analysen.

---

## 🚀 Installation & Setup

### Voraussetzungen
- Docker & Docker Compose
- Node.js 18+ (Für das Frontend)
- Python 3.11+
- Ollama (Lokal installiert)

### 1. Datenbank starten
Die gesamte Infrastruktur läuft über PostgreSQL.
```bash
sudo docker compose up -d
```

### 2. Backend starten
```bash
# Virtuelles Environment erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Server starten
uvicorn app.main_api:app --reload --port 8000 --host 0.0.0.0
```

### 3. Frontend starten
```bash
cd web
npm install
npm run dev -- -H 0.0.0.0
```

### 4. Lokalen KI-Mentor starten (Ollama)
In einem neuen Terminalfenster:
```bash
ollama run llama3
```
*(Das Backend verbindet sich standardmäßig mit `localhost:11434`)*

---

## 🔐 Umgebungsvariablen (`.env`)

Kopiere `.env.example` in `.env` und befülle die Keys:
```env
# Börsen API Keys
BINANCE_API_KEY=dein_key
BINANCE_SECRET_KEY=dein_secret
KUCOIN_API_KEY=dein_key
...

# Trading Setup
LIVE_TRADING=false
TRADE_AMOUNT_USDT=20

# Ollama Setup
OLLAMA_URL=http://localhost:11434/api/chat
OLLAMA_MODEL=llama3
```

---

## 🛑 Haftungsausschluss (Disclaimer)
*Dieses System ist ein experimentelles Tool für den automatisierten algorithmischen Handel. Kryptowährungen unterliegen starken Schwankungen. Die Nutzung dieses Systems (insbesondere der "Live Trading" Modus) erfolgt auf eigene Gefahr. Die Entwickler übernehmen keine Haftung für finanzielle Verluste.*
