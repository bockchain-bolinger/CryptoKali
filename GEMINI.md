# CryptoKali Ultimate

CryptoKali is a modular, high-performance crypto research and screening suite designed for Binance Spot and USDT-M Futures markets. It integrates data fetching, technical analysis, regime detection, and backtesting capabilities, exposed via a FastAPI backend and a Streamlit dashboard.

## Core Components
- **Data:** Connectors for Binance Spot and USDT-M Futures (via `ccxt`) and derivative metrics (Funding, Open Interest, Liquidations).
- **Core Engine:** Includes indicator calculations, regime detection, risk management, trade management, and various trading strategy modules.
- **Live/Scanner:** Scheduler-based live scanner with alert capabilities (Telegram, Discord, Webhooks).
- **Backtest:** Simulation engine for testing strategies with realistic fee and slippage modeling.
- **API/Dashboard:** FastAPI service for backend operations and Streamlit for UI/dashboarding.

## Development & Operations
- **Environment:** Python 3.13+ (`requirements.txt`).
- **Dependencies:** `fastapi`, `ccxt`, `pandas`, `ta`, `streamlit`, `apscheduler`.
- **Run API:** `uvicorn app.main_api:app --reload`
- **Run Scheduler:** `python -m app.live.run_scheduler`
- **Run Dashboard:** `streamlit run dashboard/dashboard.py`

## Conventions
- **Naming:** Follow PEP 8.
- **Async:** Use `async/await` for IO-bound operations (API calls).
- **Structure:** Modular structure under `app/`.
