import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Fallback to local Docker setup if not provided in ENV
DB_URL = os.getenv("DATABASE_URL", "postgresql://cryptokali:password123@localhost:5432/cryptokali")

def connect():
    try:
        return psycopg2.connect(DB_URL)
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {e}")
        # Fallback to SQLite during transition or test if needed
        import sqlite3
        from app.config import settings
        return sqlite3.connect(settings.DB_PATH)

def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
      id SERIAL PRIMARY KEY,
      ts TEXT NOT NULL,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      strategy TEXT NOT NULL,
      score REAL NOT NULL,
      entry REAL,
      stop REAL,
      tp1 REAL,
      tp2 REAL,
      tags TEXT,
      meta_json TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
      id SERIAL PRIMARY KEY,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      strategy TEXT NOT NULL,
      last_sent_ts TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS backtests (
      id SERIAL PRIMARY KEY,
      ts TEXT NOT NULL,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      strategy TEXT NOT NULL,
      trades INTEGER NOT NULL,
      winrate REAL NOT NULL,
      profit_factor REAL NOT NULL,
      max_dd REAL NOT NULL,
      expectancy REAL NOT NULL,
      net_pnl REAL NOT NULL,
      meta_json TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS positions (
      id SERIAL PRIMARY KEY,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      direction TEXT NOT NULL,
      size REAL NOT NULL,
      entry_price REAL NOT NULL,
      stop_price REAL,
      tp1 REAL,
      tp2 REAL,
      status TEXT NOT NULL,
      created_ts TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
      id SERIAL PRIMARY KEY,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      order_id TEXT NOT NULL,
      direction TEXT NOT NULL,
      price REAL NOT NULL,
      size REAL NOT NULL,
      status TEXT NOT NULL,
      created_ts TEXT NOT NULL
    );
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS paper_trades (
      id SERIAL PRIMARY KEY, 
      ts TEXT, 
      symbol TEXT, 
      side TEXT, 
      entry_price REAL, 
      size REAL, 
      stop REAL, 
      tp1 REAL, 
      tp2 REAL, 
      strategy TEXT, 
      status TEXT DEFAULT 'open', 
      exit_price REAL, 
      pnl REAL
    );
    """)

    con.commit()
    con.close()

def save_order(venue, symbol, order_id, direction, price, size, status):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO orders (venue, symbol, order_id, direction, price, size, status, created_ts) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)",
                (venue, symbol, order_id, direction, price, size, status))
    con.commit()
    con.close()

def save_position(venue, symbol, direction, size, entry_price, stop_price, tp1, tp2, status):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO positions (venue, symbol, direction, size, entry_price, stop_price, tp1, tp2, status, created_ts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)",
                (venue, symbol, direction, size, entry_price, stop_price, tp1, tp2, status))
    con.commit()
    con.close()

def save_paper_trade(trade_data: dict) -> int:
    con = connect()
    cur = con.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    cur.execute("""
        INSERT INTO paper_trades 
        (ts, symbol, side, entry_price, size, stop, tp1, tp2, strategy, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        ts, 
        trade_data.get("symbol"), 
        trade_data.get("side"), 
        trade_data.get("entry_price"), 
        trade_data.get("size"), 
        trade_data.get("stop"), 
        trade_data.get("tp1"), 
        trade_data.get("tp2"), 
        trade_data.get("strategy"), 
        "open"
    ))
    trade_id = cur.fetchone()[0]
    con.commit()
    con.close()
    return trade_id

def get_paper_trades(status='open') -> list:
    con = connect()
    try:
        # PostgreSQL specific Dict Cursor
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM paper_trades WHERE status=%s", (status,))
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        # Fallback for SQLite
        cur = con.cursor()
        cur.execute("SELECT * FROM paper_trades WHERE status=?", (status,))
        rows = cur.fetchall()
        col_names = [description[0] for description in cur.description]
        trades = []
        for row in rows:
            trades.append(dict(zip(col_names, row)))
        return trades
    finally:
        con.close()

def close_paper_trade(trade_id: int, exit_price: float) -> float:
    con = connect()
    cur = con.cursor()
    
    # Needs to handle both %s (Postgres) and ? (SQLite)
    placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
    
    cur.execute(f"SELECT side, entry_price, size FROM paper_trades WHERE id={placeholder} AND status='open'", (trade_id,))
    row = cur.fetchone()
    
    if not row:
        con.close()
        return 0.0
        
    # sqlite returns tuple, psycopg2 might return realdict depending on setup, but we use standard cursor here
    side = row[0] if isinstance(row, tuple) else row['side']
    entry_price = row[1] if isinstance(row, tuple) else row['entry_price']
    size = row[2] if isinstance(row, tuple) else row['size']
    
    if side.lower() == 'buy' or side.lower() == 'long':
        pnl = (exit_price - entry_price) * size
    else:
        pnl = (entry_price - exit_price) * size
        
    cur.execute(f"""
        UPDATE paper_trades 
        SET status='closed', exit_price={placeholder}, pnl={placeholder} 
        WHERE id={placeholder}
    """, (exit_price, pnl, trade_id))
    
    con.commit()
    con.close()
    return pnl

def get_historical_win_rate() -> float:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT pnl FROM paper_trades WHERE status='closed'")
    rows = cur.fetchall()
    con.close()
    
    if not rows:
        return 0.45 # Default fallback
        
    # row[0] will be the PNL
    wins = sum(1 for r in rows if (r[0] if isinstance(r, tuple) else r['pnl']) > 0)
    total = len(rows)
    return wins / total
