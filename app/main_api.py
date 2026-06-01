from fastapi import FastAPI, Query
from app.db import init_db, connect
from app.live.scanner import scan_once
import json

app = FastAPI(title="CryptoKali Ultimate (Binance Spot + Futures)")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/scan")
def scan():
    return {"results": scan_once()}

@app.get("/top")
def top(limit: int = Query(50, ge=1, le=500)):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT ts, venue, symbol, timeframe, strategy, score, entry, stop, tp1, tp2, tags, meta_json FROM scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    con.close()
    items = []
    for r in rows:
        items.append({
            "ts": r[0], "venue": r[1], "symbol": r[2], "timeframe": r[3], "strategy": r[4], "score": r[5],
            "entry": r[6], "stop": r[7], "tp1": r[8], "tp2": r[9], "tags": r[10],
            "meta": json.loads(r[11]) if r[11] else {}
        })
    return {"items": items}
