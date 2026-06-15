# Apex AI (formerly CryptoKali) 🚀

![Apex AI Banner](https://img.shields.io/badge/Status-Feature_Complete-success?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white) ![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)

Apex AI is an institutional-grade, fully autonomous algorithmic trading and research framework. It is designed to replace human emotion with pure mathematics, real-time machine learning, and multi-agent AI orchestration.

---

## 🌟 Key Features

### 1. Multi-Agent AI Swarm (MoE)
A specialized "Mixture of Experts" architecture coordinates trading decisions:
- **Market Analyst Agent:** Processes raw OHLCV and technical indicators to establish a market bias.
- **Risk Agent:** Applies the Kelly Criterion and strict risk constraints to protect capital.
- **Sentiment & News Agent:** Evaluates the global Crypto Fear & Greed Index and real-time news via CryptoPanic.
- **Coordinator Agent:** Orchestrates the swarm, weighing all inputs to issue the final `GO / NO-GO` execution command.

### 2. Machine Learning Predictor
- Uses an embedded `Random Forest Classifier` (scikit-learn).
- Real-time feature engineering (Returns, RSI, MACD, Volatility).
- Continuously trains on historical data to predict the next candle's trend probability.

### 3. Institutional Risk Management
- **PyPortfolioOpt Integration:** Utilizes Modern Portfolio Theory (MPT).
- Automatically calculates the **Max Sharpe Ratio** allocation based on the covariance matrix of active positions, ensuring the portfolio is mathematically balanced.

### 4. Smart Order Routing (SOR) & Arbitrage
- Real-time, asynchronous orderbook scanning via CCXT.
- The `Execution Agent` automatically routes orders to the exchange with the lowest slippage (Binance, KuCoin, Bitget).
- Embedded Arbitrage Radar constantly scans for cross-exchange inefficiencies and visualizes profitable spreads.

### 5. Apex Evolution (Continuous Learning)
- A self-improving RAG (Retrieval-Augmented Generation) pipeline.
- Performs an automated LLM "Post-Mortem" autopsy every time a trade closes.
- Extracts actionable lessons and stores them in the `trade_lessons` database to prevent repeating the same mistakes.

### 6. "What-If" Macro Simulator
- A sandbox to simulate macroeconomic shocks.
- Tweak the US Dollar Index (DXY) or FED Interest Rates to see real-time AI projections on Bitcoin, Ethereum, and DeFi TVL, accompanied by an institutional flash report.

### 7. Futuristic Dashboard
- A sleek, Next.js-powered Glassmorphism UI.
- Live WebSockets for Ticker and Chatbot integration.
- Includes sub-dashboards for Portfolio Management, AI Chat, Arbitrage, Strategy Lab, and Macroeconomics.

---

## 🛠 Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, APScheduler.
- **Data & ML:** Pandas, NumPy, Scikit-Learn, PyPortfolioOpt, TA-Lib.
- **Exchange Connectivity:** CCXT (async).
- **Database:** PostgreSQL (with TimescaleDB extension recommended).
- **Frontend:** Next.js 14, React, Lucide-Icons, Lightweight Charts.
- **AI Core:** OpenAI GPT-4o, local Ollama fallbacks.

---

## 🚀 Quick Start

1. **Start the PostgreSQL Database:** Ensure your database is running and the `DATABASE_URL` is set in the `.env`.
2. **Start the Backend:**
   ```bash
   cd /home/artuirik/Schreibtisch/CryptoKali
   source .venv/bin/activate
   uvicorn app.main_api:app --reload
   ```
3. **Start the Frontend:**
   ```bash
   cd /home/artuirik/Schreibtisch/CryptoKali/web
   npm run dev
   ```
4. Open `http://localhost:3000` in your browser.

*(For a detailed breakdown of the system architecture, see `DOCS.md`)*
