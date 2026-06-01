import requests
from datetime import datetime, timezone
from app.config import settings
from app.db import connect

def _now():
    return datetime.now(timezone.utc).isoformat()

def can_send(venue: str, symbol: str, strategy: str, cooldown_min: int = 45) -> bool:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT last_sent_ts FROM alerts WHERE venue=? AND symbol=? AND strategy=? LIMIT 1", (venue, symbol, strategy))
    row = cur.fetchone()
    con.close()
    if not row:
        return True
    last = datetime.fromisoformat(row[0])
    delta_min = (datetime.now(timezone.utc) - last).total_seconds() / 60.0
    return delta_min >= cooldown_min

def mark_sent(venue: str, symbol: str, strategy: str):
    con = connect()
    cur = con.cursor()
    cur.execute("DELETE FROM alerts WHERE venue=? AND symbol=? AND strategy=?", (venue, symbol, strategy))
    cur.execute("INSERT INTO alerts(venue, symbol, strategy, last_sent_ts) VALUES(?,?,?,?)", (venue, symbol, strategy, _now()))
    con.commit()
    con.close()

def send_telegram(text: str) -> bool:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text})
    return r.status_code == 200

def send_discord(text: str) -> bool:
    if not settings.DISCORD_WEBHOOK_URL:
        return False
    r = requests.post(settings.DISCORD_WEBHOOK_URL, json={"content": text})
    return r.status_code in (200, 204)

def send_webhook(payload: dict) -> bool:
    if not settings.GENERIC_WEBHOOK_URL:
        return False
    r = requests.post(settings.GENERIC_WEBHOOK_URL, json=payload, timeout=12)
    return r.status_code in (200, 201, 202, 204)
