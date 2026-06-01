import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from app.db import connect
import re

ANN_URLS = [
    "https://www.binance.com/en/support/announcement/c-48?navId=48",
    "https://www.binance.com/en/support/announcement/c-49?navId=49",
]

def _now():
    return datetime.now(timezone.utc).isoformat()

def _store_event(source: str, title: str, url: str, tags: str = ""):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO catalyst_events(ts, source, title, url, tags) VALUES(?,?,?,?,?)",
        (_now(), source, title, url, tags),
    )
    con.commit()
    con.close()

def _known_titles_set():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT title FROM catalyst_events ORDER BY id DESC LIMIT 500")
    rows = cur.fetchall()
    con.close()
    return set(r[0] for r in rows)

def poll_binance_announcements():
    known = _known_titles_set()
    new_items = []
    for src in ANN_URLS:
        try:
            html = requests.get(src, timeout=12).text
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = (a.get_text() or "").strip()
                if not title or len(title) < 12:
                    continue
                if "/support/announcement/" not in href:
                    continue
                url = href
                if url.startswith("/"):
                    url = "https://www.binance.com" + url
                if title in known:
                    continue
                tags = "listing" if re.search(r"\blist(ing)?\b", title.lower()) else ""
                _store_event("binance_announcement", title, url, tags=tags)
                new_items.append({"source": "binance_announcement", "title": title, "url": url, "tags": tags})
        except Exception:
            continue
    return new_items

def catalyst_score_for_symbol(symbol: str, lookback_events: int = 200) -> float:
    token = symbol.split("/")[0].upper()
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT title FROM catalyst_events ORDER BY id DESC LIMIT ?", (lookback_events,))
    titles = [r[0] for r in cur.fetchall()]
    con.close()
    for t in titles:
        if re.search(rf"\b{re.escape(token)}\b", t.upper()):
            return 1.0
    return 0.0
