import asyncio
import json
import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

from app.db import save_paper_trade, get_paper_trades, close_paper_trade, init_db
from app.chat.handler import ChatHandler
from app.agents.coordinator import CoordinatorAgent
from app.data.sentiment import get_fear_greed_index, get_crypto_news, calculate_news_sentiment
from app.data.macro import get_macro_data
from app.data.onchain import get_onchain_data
from app.data.whale_tracker import whale_tracker
from app.data.arbitrage_scanner import arbitrage_scanner
from app.agents.execution_agent import ExecutionAgent
import ccxt
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pandas as pd
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Initialize DB
init_db()

# Auto-Scanner Logic
scheduler = AsyncIOScheduler()
execution_agent = ExecutionAgent()

async def run_market_scan():
    logger.info("Starting automated market scan (1h timeframe)...")
    try:
        exchange = ccxt.binance()
        # Vorerst nur eine kleine Liste an Top-Coins für den Test
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']
        
        for symbol in symbols:
            # Hole 1h OHLCV Daten
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Analyse mit Coordinator
            result = coordinator_agent.analyze({"symbol": symbol, "df": df})
            
            # Wenn starkes GO-Signal -> Trade ausführen (Live oder Paper)
            if result.get("recommendation") == "GO":
                current_price = float(df['close'].iloc[-1])
                bias = result.get("agent_results", {}).get("market_analyst", {}).get("bias", "neutral")
                
                # Einfaches Risk-Management
                side = "LONG" if bias == "bullish" else "SHORT"
                stop = current_price * 0.95 if side == "LONG" else current_price * 1.05
                tp1 = current_price * 1.10 if side == "LONG" else current_price * 0.90
                
                # Versuch Live Trade auszuführen (fällt auf Paper zurück wenn keys/live_trading fehlen)
                exec_result = await execution_agent.execute_trade(
                    symbol=symbol,
                    side=side,
                    current_price=current_price,
                    stop_loss=stop,
                    take_profit=tp1
                )
                
                db_status = "open"
                if exec_result.get("status") == "error":
                    db_status = "failed"
                
                trade_data = {
                    "symbol": symbol,
                    "side": side,
                    "entry_price": exec_result.get("entry_price", current_price),
                    "stop": float(stop),
                    "tp1": float(tp1),
                    "tp2": float(tp1 * 1.05 if side == "LONG" else tp1 * 0.95),
                    "size": float(result.get("size", 0.1)),
                    "strategy": result.get("chosen_strategy", "ai_coordinator_1h"),
                    "status": db_status
                }
                trade_id = save_paper_trade(trade_data) # Wir speichern Live-Trades vorerst in derselben Tabelle zum Tracken
                
                if exec_result.get("status") == "live_executed":
                    logger.info(f"🚀 LIVE TRADE EXECUTED: {side} {symbol} @ {trade_data['entry_price']} (DB ID: {trade_id})")
                else:
                    logger.info(f"📝 PAPER TRADE SAVED: {side} {symbol} @ {trade_data['entry_price']} (DB ID: {trade_id})")
                
    except Exception as e:
        logger.error(f"Scanner error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Background Tasks
    scheduler.add_job(run_market_scan, 'interval', minutes=15)
    scheduler.start()
    
    # Start Whale Tracker WS
    asyncio.create_task(whale_tracker.start_tracking())
    
    # Start Arbitrage Scanner
    asyncio.create_task(arbitrage_scanner.start_scanning())
    
    yield
    # Cleanup
    scheduler.shutdown()
    whale_tracker.stop()
    await arbitrage_scanner.stop()

app = FastAPI(title="Apex AI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class AnalyzeRequest(BaseModel):
    symbol: str = "BTC/USDT"
    timeframe: str = "1h"

class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: dict = {}

class PaperTradeRequest(BaseModel):
    symbol: str
    side: str  # buy/sell
    entry_price: float
    stop: float
    tp1: float
    tp2: float
    size: float
    strategy: str = "manual"

# Instances
chat_handler = ChatHandler()
coordinator_agent = CoordinatorAgent()

# Helper for prices
def get_mock_prices():
    return {
        "btc": {"price": 65000.0 + random.uniform(-100, 100), "change_24h": random.uniform(-5, 5)},
        "eth": {"price": 3500.0 + random.uniform(-10, 10), "change_24h": random.uniform(-5, 5)},
        "bnb": {"price": 600.0 + random.uniform(-2, 2), "change_24h": random.uniform(-5, 5)}
    }

# Endpoints
@app.get("/health")
def health():
    return {"ok": True, "timestamp": datetime.now(timezone.utc).isoformat(), "version": "1.0.0"}

@app.get("/api/v1/scan")
def scan():
    return {"results": [{"symbol": "BTC/USDT", "score": 85, "strategy": "momentum"}]}

@app.get("/api/v1/top")
def get_top(limit: int = 50):
    return {"items": [{"symbol": "BTC/USDT", "volume": 1000000}, {"symbol": "ETH/USDT", "volume": 500000}][:limit]}

@app.get("/api/v1/signals")
def get_signals(limit: int = 50, venue: str = "", strategy: str = "", min_score: float = 0):
    return {"signals": [{"symbol": "BTC/USDT", "score": 90, "direction": "long"}][:limit]}

@app.get("/api/v1/market/overview")
def market_overview():
    try:
        exchange = ccxt.binance()
        tickers = exchange.fetch_tickers(['BTC/USDT', 'ETH/USDT', 'BNB/USDT'])
        prices = {
            "btc": {"price": tickers['BTC/USDT']['last'], "change_24h": tickers['BTC/USDT'].get('percentage', 0)},
            "eth": {"price": tickers['ETH/USDT']['last'], "change_24h": tickers['ETH/USDT'].get('percentage', 0)},
            "bnb": {"price": tickers['BNB/USDT']['last'], "change_24h": tickers['BNB/USDT'].get('percentage', 0)}
        }
    except Exception as e:
        logger.warning(f"Failed to fetch from CCXT, using mock data. Error: {e}")
        prices = get_mock_prices()
        
    fg = get_fear_greed_index()
    return {
        **prices,
        "fear_greed": {"value": fg["value"], "label": fg["value_classification"]},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v1/indicators/{symbol}")
def get_indicators(symbol: str, timeframe: str = "1h"):
    symbol = symbol.replace("-", "/")
    return {"symbol": symbol, "timeframe": timeframe, "data": {"rsi": 45, "macd": 1.2, "sma_20": 64000}}

@app.post("/api/v1/analyze")
def analyze(req: AnalyzeRequest):
    # Mocking a dataframe for the coordinator, realistically we'd fetch actual data
    df = None 
    res = coordinator_agent.analyze({"symbol": req.symbol, "df": df})
    return {"symbol": req.symbol, "analysis": res}

@app.get("/api/v1/sentiment")
def sentiment():
    fg = get_fear_greed_index()
    news = get_crypto_news()
    news_sent = calculate_news_sentiment(news)
    return {
        "fear_greed": fg,
        "news_sentiment": round(news_sent, 3),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v1/news")
def news(limit: int = 20):
    news_items = get_crypto_news()
    return {"items": news_items[:limit]}

@app.get("/api/v1/portfolio")
def portfolio():
    trades = get_paper_trades()
    positions_count = len(trades)
    heat_level = "low"
    if positions_count > 5: heat_level = "high"
    elif positions_count > 2: heat_level = "medium"
    
    return {
        "equity": 10000.0, 
        "positions_count": positions_count, 
        "open_pnl": sum([random.uniform(-10, 10) for _ in trades]), 
        "heat_level": heat_level
    }

@app.get("/api/v1/macro")
def macro():
    return get_macro_data()

@app.post("/api/v1/macro/simulate")
async def simulate_macro(request: Request):
    try:
        data = await request.json()
        dxy_change = float(data.get("dxy_change_pct", 0.0))
        rate_change = float(data.get("rate_change_pct", 0.0))
        
        from app.agents.macro_agent import macro_agent
        result = await macro_agent.simulate_scenario(dxy_change, rate_change)
        return result
    except Exception as e:
        logger.error(f"Macro Simulator Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/onchain")
def onchain():
    return get_onchain_data()

@app.get("/api/v1/whales")
def whales():
    return whale_tracker.get_latest_data()

@app.get("/api/v1/arbitrage")
def get_arbitrage():
    return arbitrage_scanner.get_latest_opportunities()

@app.post("/api/v1/arbitrage/reject/{opp_id}")
def reject_arbitrage(opp_id: str):
    arbitrage_scanner.reject_opportunity(opp_id)
    return {"status": "rejected", "opp_id": opp_id}

@app.get("/api/v1/positions")
def positions():
    return {"positions": get_paper_trades()}

@app.get("/api/v1/orders/paper")
def get_paper():
    return {"trades": get_paper_trades()}

@app.post("/api/v1/orders/paper")
def create_paper_trade(req: PaperTradeRequest):
    trade_id = save_paper_trade(req.dict())
    return {"id": trade_id, "status": "open", **req.dict()}

@app.post("/api/v1/orders/paper/{trade_id}/close")
async def close_trade_api(trade_id: int, request: Request):
    try:
        data = await request.json()
        exit_price = data.get("exit_price", 0.0)
        
        # 1. Close trade in DB
        pnl = close_paper_trade(trade_id, exit_price)
        
        # 2. Trigger Evolution Post-Mortem asynchronously
        from app.agents.evolution_agent import evolution_agent
        # We need symbol, entry, side for post-mortem
        # Since close_paper_trade doesn't return everything, we just mock the details or fetch them
        # For simplicity in API, assume we pass basic info via request or fetch it
        symbol = data.get("symbol", "UNKNOWN")
        entry_price = data.get("entry_price", 0.0)
        side = data.get("side", "LONG")
        
        asyncio.create_task(evolution_agent.run_post_mortem(trade_id, symbol, entry_price, exit_price, side, pnl))
        
        return {"status": "success", "trade_id": trade_id, "pnl": pnl}
    except Exception as e:
        logger.error(f"Error closing trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/evolution/lessons")
def get_lessons():
    from app.db import get_trade_lessons
    return get_trade_lessons(limit=20)

@app.get("/api/v1/agents/status")
def agents_status():
    agents = [coordinator_agent, coordinator_agent.market_analyst, coordinator_agent.risk_agent, coordinator_agent.sentiment_agent, coordinator_agent.news_agent, coordinator_agent.portfolio_agent]
    return {"agents": [{"name": a.name, "description": a.description, "status": "online"} for a in agents]}

@app.post("/api/v1/chat")
def chat(req: ChatRequest):
    res = chat_handler.process_message(req.session_id, req.message, req.context)
    return {"session_id": req.session_id, **res}

@app.get("/api/v1/chat/history/{session_id}")
def get_chat_history(session_id: str):
    return {"messages": chat_handler.history.get_history(session_id)}

@app.delete("/api/v1/chat/{session_id}")
def clear_chat(session_id: str):
    chat_handler.history.clear_session(session_id)
    return {"ok": True}

@app.get("/api/v1/heatmap")
def heatmap():
    return {"coins": [
        {"symbol": "BTC/USDT", "price": 65000, "change_24h": 2.5, "volume": 1000000},
        {"symbol": "ETH/USDT", "price": 3500, "change_24h": -1.2, "volume": 500000}
    ]}

@app.get("/api/v1/strategies")
def get_strategies():
    return {"strategies": ["s1_momentum_breakout", "s2_mean_reversion"]}

@app.get("/api/v1/backtest/{strategy}")
async def run_backtest_old(strategy: str):
    # Backward compatibility mock
    return {"message": "Use POST /api/v1/backtest/run instead", "strategy": strategy}

@app.post("/api/v1/lab/experiment/run")
async def run_experiment(request: Request):
    try:
        data = await request.json()
        experiment_name = data.get("name", "Auto Experiment")
        venue = data.get("venue", "binance")
        symbol = data.get("symbol", "BTC/USDT")
        timeframe = data.get("timeframe", "1h")
        strategy = data.get("strategy", "MACD_Cross")
        
        from app.core.experiment_lab import lab
        result = lab.run_experiment(experiment_name, venue, symbol, timeframe, strategy)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except Exception as e:
        logger.error(f"Error running experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/lab/experiments")
async def get_experiments():
    from app.db import get_experiment_runs
    return get_experiment_runs()

@app.post("/api/v1/lab/experiment/{run_id}/promote")
async def promote_experiment_endpoint(run_id: int, request: Request):
    try:
        data = await request.json()
        new_status = data.get("status", "paper")
        
        from app.db import promote_experiment
        success = promote_experiment(run_id, new_status)
        if not success:
            raise HTTPException(status_code=404, detail="Experiment run not found")
            
        return {"status": "success", "run_id": run_id, "new_status": new_status}
    except Exception as e:
        logger.error(f"Error promoting experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/strategies/active")
async def active_strategies():
    from app.db import get_active_strategies
    return get_active_strategies()

@app.post("/api/v1/ml/train")
async def train_ml_model(request: Request):
    try:
        data = await request.json()
        symbol = data.get("symbol", "BTC/USDT")
        timeframe = data.get("timeframe", "1h")
        
        from app.agents.predictor_agent import predictor
        result = predictor.train_model(symbol, timeframe)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except Exception as e:
        logger.error(f"Error training ML model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ml/predict/{symbol:path}")
async def predict_ml(symbol: str, timeframe: str = "1h"):
    try:
        from app.agents.predictor_agent import predictor
        result = predictor.predict(symbol, timeframe)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except Exception as e:
        logger.error(f"Error making ML prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/risk/status")
async def get_risk_status():
    from app.core.sentinel import sentinel
    return sentinel.get_status()

@app.post("/api/v1/portfolio/optimize")
async def optimize_portfolio(request: Request):
    try:
        data = await request.json()
        symbols = data.get("symbols", ["BTC/USDT", "ETH/USDT"])
        from app.core.sentinel import sentinel
        result = sentinel.get_optimal_allocation(symbols)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/arbitrage/scan")
async def scan_arbitrage():
    try:
        from app.core.sor_engine import sor_engine
        results = await sor_engine.scan_arbitrage()
        return results
    except Exception as e:
        logger.error(f"Error scanning arbitrage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/data/fetch-historical")
async def fetch_historical(request: Request):
    try:
        data = await request.json()
        venue = data.get("venue", "binance")
        symbol = data.get("symbol", "BTC/USDT")
        timeframe = data.get("timeframe", "1h")
        candles = data.get("candles", 1000)
        
        from app.data.historical_loader import fetch_historical_ohlcv
        count = await fetch_historical_ohlcv(venue, symbol, timeframe, limit=candles)
        
        return {"status": "success", "fetched": count}
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/backtest/run")
async def run_backtest_new(request: Request):
    try:
        data = await request.json()
        venue = data.get("venue", "binance")
        symbol = data.get("symbol", "BTC/USDT")
        timeframe = data.get("timeframe", "1h")
        strategy = data.get("strategy", "MACD_Cross")
        
        from app.core.auditor import auditor_engine
        result = auditor_engine.run_backtest(venue, symbol, timeframe, strategy)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager_ticker = ConnectionManager()
manager_signals = ConnectionManager()

@app.websocket("/ws/ticker")
async def ws_ticker(websocket: WebSocket):
    await manager_ticker.connect(websocket)
    try:
        while True:
            prices = get_mock_prices()
            data = {
                "btc_price": prices["btc"]["price"],
                "eth_price": prices["eth"]["price"],
                "bnb_price": prices["bnb"]["price"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager_ticker.disconnect(websocket)

@app.websocket("/ws/signals")
async def ws_signals(websocket: WebSocket):
    await manager_signals.connect(websocket)
    try:
        while True:
            data = {"signals": [{"symbol": "BTC/USDT", "score": 90, "direction": "long"}]}
            await websocket.send_json(data)
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        manager_signals.disconnect(websocket)

@app.websocket("/ws/chat/{session_id}")
async def ws_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            res = chat_handler.process_message(session_id, data)
            await websocket.send_json({
                "response_text": res["response_text"],
                "agent_used": res["agent_used"]
            })
    except WebSocketDisconnect:
        pass
