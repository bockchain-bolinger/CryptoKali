import streamlit as st
import sqlite3
import pandas as pd
from app.config import settings
from app.trade.portfolio import sync_portfolio

st.set_page_config(page_title="CryptoKali Dashboard", layout="wide")
st.title("CryptoKali Ultimate Dashboard")

# Navigation
tab1, tab2 = st.tabs(["Trade Plans", "Portfolio Tracker"])

@st.cache_data(ttl=15)
def load_scans(limit=1500):
    con = sqlite3.connect(settings.DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM scans ORDER BY id DESC LIMIT {limit}", con)
    con.close()
    return df

@st.cache_data(ttl=60)
def load_positions():
    con = sqlite3.connect(settings.DB_PATH)
    df = pd.read_sql_query("SELECT * FROM positions WHERE status = 'open'", con)
    con.close()
    return df

with tab1:
    df = load_scans()
    if df.empty:
        st.warning("No scans yet. Run /scan or scheduler.")
    else:
        df["score"] = pd.to_numeric(df["score"], errors="coerce")
        venues = sorted(df["venue"].unique().tolist())
        strategies = sorted(df["strategy"].unique().tolist())

        c1, c2, c3 = st.columns(3)
        with c1:
            venue_sel = st.multiselect("Venues", venues, default=venues)
        with c2:
            strat_sel = st.multiselect("Strategies", strategies, default=strategies)
        with c3:
            min_score = st.slider("Min score", 0, 100, 75)

        f = df[df["venue"].isin(venue_sel) & df["strategy"].isin(strat_sel) & (df["score"] >= min_score)]
        st.subheader("Latest trade plans")
        st.dataframe(f[["ts","venue","symbol","timeframe","strategy","score","entry","stop","tp1","tp2","tags"]], use_container_width=True)
        st.subheader("Score distribution")
        st.bar_chart(f["score"].value_counts().sort_index())

with tab2:
    st.subheader("Live Positions")
    if st.button("Sync Portfolio"):
        with st.spinner("Syncing with Binance..."):
            sync_portfolio()
            st.success("Synced!")
    
    pos = load_positions()
    if pos.empty:
        st.info("No open positions.")
    else:
        st.dataframe(pos[["venue","symbol","direction","size","entry_price","created_ts"]], use_container_width=True)

