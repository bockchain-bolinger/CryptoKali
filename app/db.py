import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Fallback to local Docker setup if not provided in ENV
DB_URL = os.getenv("DATABASE_URL", "postgresql://apex_ai:password123@localhost:5432/apex_ai")

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trade_lessons (
            id SERIAL PRIMARY KEY,
            trade_id INTEGER,
            symbol TEXT,
            pnl REAL,
            market_context TEXT,
            lesson_learned TEXT,
            timestamp BIGINT
        )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS historical_ohlcv (
      id SERIAL PRIMARY KEY,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      timestamp BIGINT NOT NULL,
      open REAL NOT NULL,
      high REAL NOT NULL,
      low REAL NOT NULL,
      close REAL NOT NULL,
      volume REAL NOT NULL,
      UNIQUE(venue, symbol, timeframe, timestamp)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      description TEXT,
      created_at TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS experiment_runs (
      id SERIAL PRIMARY KEY,
      experiment_name TEXT NOT NULL,
      strategy TEXT NOT NULL,
      symbol TEXT NOT NULL,
      timeframe TEXT NOT NULL,
      metrics_json TEXT NOT NULL,
      ai_finding TEXT,
      created_at TEXT NOT NULL,
      status TEXT DEFAULT 'research'
    );
    """)

    # Try to add status column if it doesn't exist (for SQLite/Postgres backwards compatibility)
    try:
        cur.execute("ALTER TABLE experiment_runs ADD COLUMN status TEXT DEFAULT 'research';")
    except Exception:
        con.rollback() if isinstance(con, psycopg2.extensions.connection) else None

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

def save_trade_lesson(trade_id: int, symbol: str, pnl: float, market_context: str, lesson_learned: str) -> int:
    import time
    con = connect()
    cur = con.cursor()
    
    placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
    
    query = f"""
        INSERT INTO trade_lessons (trade_id, symbol, pnl, market_context, lesson_learned, timestamp)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        RETURNING id
    """
    
    if not isinstance(con, psycopg2.extensions.connection):
        query = query.replace("RETURNING id", "")
        
    cur.execute(query, (trade_id, symbol, pnl, market_context, lesson_learned, int(time.time() * 1000)))
    
    if isinstance(con, psycopg2.extensions.connection):
        lesson_id = cur.fetchone()[0]
    else:
        lesson_id = cur.lastrowid
        
    con.commit()
    con.close()
    return lesson_id

def get_trade_lessons(symbol: str = None, limit: int = 10):
    con = connect()
    cur = con.cursor(cursor_factory=RealDictCursor) if isinstance(con, psycopg2.extensions.connection) else con.cursor()
    
    query = "SELECT * FROM trade_lessons"
    params = []
    
    if symbol:
        placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
        query += f" WHERE symbol = {placeholder}"
        params.append(symbol)
        
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    con.close()
    
    if isinstance(con, psycopg2.extensions.connection):
        return [dict(row) for row in rows]
    else:
        col_names = [description[0] for description in cur.description]
        return [dict(zip(col_names, row)) for row in rows]

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

def save_historical_candles(venue: str, symbol: str, timeframe: str, ohlcv_data: list):
    con = connect()
    cur = con.cursor()
    # ohlcv_data is a list of [timestamp, open, high, low, close, volume]
    
    # We use ON CONFLICT DO NOTHING for postgres
    # For sqlite we would use INSERT OR IGNORE, but since we migrated to Postgres mainly:
    insert_query = """
        INSERT INTO historical_ohlcv (venue, symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (venue, symbol, timeframe, timestamp) DO NOTHING
    """
    
    # Fallback to SQLite syntax if we are using sqlite fallback
    if not isinstance(con, psycopg2.extensions.connection):
        insert_query = """
            INSERT OR IGNORE INTO historical_ohlcv (venue, symbol, timeframe, timestamp, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    records = [
        (venue, symbol, timeframe, c[0], c[1], c[2], c[3], c[4], c[5])
        for c in ohlcv_data
    ]
    cur.executemany(insert_query, records)
    con.commit()
    con.close()

def get_historical_candles(venue: str, symbol: str, timeframe: str) -> list:
    con = connect()
    cur = con.cursor()
    
    placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
    
    cur.execute(f"""
        SELECT timestamp, open, high, low, close, volume 
        FROM historical_ohlcv 
        WHERE venue={placeholder} AND symbol={placeholder} AND timeframe={placeholder}
        ORDER BY timestamp ASC
    """, (venue, symbol, timeframe))
    
    rows = cur.fetchall()
    con.close()
    
    # Return in CCXT format: [[timestamp, o, h, l, c, v], ...]
    return [list(r) for r in rows]

def save_backtest_result(data: dict) -> int:
    con = connect()
    cur = con.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    
    placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
    
    query = f"""
        INSERT INTO backtests 
        (ts, venue, symbol, timeframe, strategy, trades, winrate, profit_factor, max_dd, expectancy, net_pnl, meta_json)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        RETURNING id
    """
    
    if not isinstance(con, psycopg2.extensions.connection):
        query = query.replace("RETURNING id", "")
        
    cur.execute(query, (
        ts,
        data.get("venue"),
        data.get("symbol"),
        data.get("timeframe"),
        data.get("strategy"),
        data.get("trades"),
        data.get("winrate"),
        data.get("profit_factor"),
        data.get("max_dd"),
        data.get("expectancy"),
        data.get("net_pnl"),
        json.dumps(data.get("meta_json", {}))
    ))
    
    if isinstance(con, psycopg2.extensions.connection):
        bt_id = cur.fetchone()[0]
    else:
        bt_id = cur.lastrowid
        
    con.commit()
    con.close()
    return bt_id

def log_experiment_run(experiment_name: str, strategy: str, symbol: str, timeframe: str, metrics: dict, ai_finding: str = "", status: str = "research") -> int:
    con = connect()
    cur = con.cursor()
    ts = datetime.now(timezone.utc).isoformat()
    
    placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
    
    query = f"""
        INSERT INTO experiment_runs 
        (experiment_name, strategy, symbol, timeframe, metrics_json, ai_finding, created_at, status)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        RETURNING id
    """
    
    if not isinstance(con, psycopg2.extensions.connection):
        query = query.replace("RETURNING id", "")
        
    cur.execute(query, (
        experiment_name,
        strategy,
        symbol,
        timeframe,
        json.dumps(metrics),
        ai_finding,
        ts,
        status
    ))
    
    if isinstance(con, psycopg2.extensions.connection):
        run_id = cur.fetchone()[0]
    else:
        run_id = cur.lastrowid
        
    con.commit()
    con.close()
    return run_id

def get_experiment_runs() -> list:
    con = connect()
    cur = con.cursor()
    
    cur.execute("""
        SELECT id, experiment_name, strategy, symbol, timeframe, metrics_json, ai_finding, created_at, status 
        FROM experiment_runs 
        ORDER BY id DESC LIMIT 50
    """)
    
    rows = cur.fetchall()
    con.close()
    
    runs = []
    for r in rows:
        if isinstance(r, tuple):
            runs.append({
                "id": r[0],
                "experiment_name": r[1],
                "strategy": r[2],
                "symbol": r[3],
                "timeframe": r[4],
                "metrics": json.loads(r[5]),
                "ai_finding": r[6],
                "created_at": r[7],
                "status": r[8] if len(r) > 8 else "research"
            })
        else:
            runs.append({
                "id": r['id'],
                "experiment_name": r['experiment_name'],
                "strategy": r['strategy'],
                "symbol": r['symbol'],
                "timeframe": r['timeframe'],
                "metrics": json.loads(r['metrics_json']),
                "ai_finding": r['ai_finding'],
                "created_at": r['created_at'],
                "status": r.get('status', 'research')
            })
            
    return runs

def promote_experiment(run_id: int, status: str) -> bool:
    con = connect()
    cur = con.cursor()
    
    placeholder = "%s" if isinstance(con, psycopg2.extensions.connection) else "?"
    cur.execute(f"UPDATE experiment_runs SET status = {placeholder} WHERE id = {placeholder}", (status, run_id))
    
    con.commit()
    con.close()
    return True

def get_active_strategies() -> list:
    con = connect()
    cur = con.cursor()
    
    cur.execute("""
        SELECT id, experiment_name, strategy, symbol, timeframe, status 
        FROM experiment_runs 
        WHERE status IN ('paper', 'live')
        ORDER BY id DESC
    """)
    
    rows = cur.fetchall()
    con.close()
    
    strategies = []
    for r in rows:
        if isinstance(r, tuple):
            strategies.append({
                "id": r[0],
                "experiment_name": r[1],
                "strategy": r[2],
                "symbol": r[3],
                "timeframe": r[4],
                "status": r[5]
            })
        else:
            strategies.append({
                "id": r['id'],
                "experiment_name": r['experiment_name'],
                "strategy": r['strategy'],
                "symbol": r['symbol'],
                "timeframe": r['timeframe'],
                "status": r['status']
            })
            
    return strategies

