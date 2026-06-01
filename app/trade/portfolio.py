from app.data.exchanges.binance import BinanceConnector
from app.db import connect, save_position

def sync_portfolio():
    connector = BinanceConnector(is_futures=True)
    positions = connector.exchange.fetch_positions()
    
    # Filter for active positions
    active_positions = [p for p in positions if float(p["contracts"]) > 0]
    
    con = connect()
    cur = con.cursor()
    # Clear old active positions to sync
    cur.execute("DELETE FROM positions WHERE status = 'open'")
    
    for p in active_positions:
        save_position(
            venue="binance",
            symbol=p["symbol"],
            direction=p["side"],
            size=float(p["contracts"]),
            entry_price=float(p["entryPrice"]),
            stop_price=None, # Not directly in fetch_positions
            tp1=None,
            tp2=None,
            status="open"
        )
    con.commit()
    con.close()
    return active_positions
