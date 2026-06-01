# CryptoKali Ultimate

CryptoKali is a modular, high-performance crypto research, screening, and automated trading suite designed for Binance Spot and USDT-M Futures markets.

## Key Features

- **Data Fetching:** Robust connectors for OHLCV, Funding, Open Interest, and Liquidations.
- **Advanced Analysis:** Technical indicator library, regime detection (ADX), and Machine Learning-based anomaly detection (`scikit-learn`).
- **Trading Engine:** Modular strategy plugin system and a dedicated Risk Management module.
- **Order Management (OMS):** Secure order placement with automated risk guardrails and persistence.
- **Portfolio Tracking:** Real-time synchronization of open positions and balances.
- **Backtesting v2:** Realistic simulation engine accounting for fees and slippage.
- **Dashboard & API:** FastAPI backend with a Streamlit UI for visualization.

## Setup

1. **Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your Binance API keys and notification settings
   ```

## Running the System

- **API Backend:** `uvicorn app.main_api:app --reload`
- **Scanner Scheduler:** `python -m app.live.run_scheduler`
- **Dashboard:** `streamlit run dashboard/dashboard.py`

## Project Structure

- `app/core/`: Indicators, strategy plugins, regime detection, and risk management.
- `app/data/`: Exchange connectors and data fetchers.
- `app/trade/`: OMS and Portfolio Tracking modules.
- `app/backtest/`: Backtesting engine with simulator.
- `tests/`: Unit test suite.

---
*Disclaimer: This is a research and screening tool. No profit guarantees. Always use safe risk management practices.*
# CrptoKali
