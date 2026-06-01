import sqlite3
from app.config import settings

def connect():
    return sqlite3.connect(settings.DB_PATH)

def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
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
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      venue TEXT NOT NULL,
      symbol TEXT NOT NULL,
      strategy TEXT NOT NULL,
      last_sent_ts TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS backtests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
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
      id INTEGER PRIMARY KEY AUTOINCREMENT,
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
      id INTEGER PRIMARY KEY AUTOINCREMENT,
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


    con.commit()
    con.close()

def save_order(venue, symbol, order_id, direction, price, size, status):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO orders (venue, symbol, order_id, direction, price, size, status, created_ts) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                (venue, symbol, order_id, direction, price, size, status))
    con.commit()
    con.close()

def save_position(venue, symbol, direction, size, entry_price, stop_price, tp1, tp2, status):
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT INTO positions (venue, symbol, direction, size, entry_price, stop_price, tp1, tp2, status, created_ts) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                (venue, symbol, direction, size, entry_price, stop_price, tp1, tp2, status))
    con.commit()
    con.close()
