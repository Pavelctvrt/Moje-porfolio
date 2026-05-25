import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Moje Portfolio", layout="wide", initial_sidebar_state="expanded")

# --- VYNUCENÍ ČERNÉHO POZADÍ A MAXIMÁLNÍ ČITELNOSTI ---
st.markdown("""
<style>
    .stApp, .main, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .stMarkdown p, .stText, label, .stMetricLabel, [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stDataFrame"] {
        background-color: #111111 !important;
    }
    footer {visibility: hidden;}
    header {background: transparent !important;}
    
    /* PÍSMO PRO ČLÁNKY - Zářivě světle modrá a tučná */
    a {color: #66b3ff !important; text-decoration: none; font-weight: 700 !important;}
    a:hover {text-decoration: underline; color: #99ccff !important;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACE PORTFOLIA V SESSION STATE ---
if 'TICKERS_1' not in st.session_state:
    st.session_state.TICKERS_1 = {
        "SXR8.DE": "SXR8.DE", "Gold": "GLD", "Meta": "META", "Tesla": "TSLA", 
        "Netflix": "NFLX", "Google": "GOOGL", "Spotify": "SPOT", "Microsoft": "MSFT", 
        "Amazon": "AMZN", "Nvidia": "NVDA", "Arm": "ARM", "AMD": "AMD", 
        "Lam Research": "LRCX", "Applied Materials": "AMAT", "Super Micro": "SMCI", 
        "Palantir": "PLTR", "Alibaba": "BABA", "McDonalds": "MCD", "Novo Nordisk": "NVO", 
        "LVMH": "MC.PA", "CVS": "CVS", "Nike": "NKE", "Starbucks": "SBUX", 
        "GameStop": "GME", "Bitcoin": "BTC-USD", "Coinbase": "COIN", "Robinhood": "HOOD"
    }

if 'TICKERS_2' not in st.session_state:
    st.session_state.TICKERS_2 = {
        "Pepsi": "PEP", "Coca Cola": "KO", "Realty Income": "O", "Pfizer": "PFE", 
        "JPMorgan": "JPM", "Uber": "UBER", "ČEZ": "CEZ.PR", "Broadcom": "AVGO", 
        "Micron": "MU", "SOFI": "SOFI", "Intel": "INTC", "QCOM": "QCOM", 
        "APP": "APP", "Serve Robotics": "SERV", "SPGI": "SPGI", "Dell": "DELL", 
        "UNH": "UNH"
    }

# --- POSTRANNÍ PANEL ---
st.sidebar.header("⚙️ Správa akcií")
st.sidebar.subheader("Přidat novou")
new_name = st.sidebar.text_input("Název (např. Apple)")
new_ticker = st.sidebar.text_input("Ticker (např. AAPL)")
target_table = st.sidebar.radio("Kam přidat?", ["Tabulka 1", "Tabulka 2"])

if st.sidebar.button("➕ Přidat akcii"):
    if new_name and new_ticker:
        if "1" in target_table:
            st.session_state.TICKERS_1[new_name] = new_ticker.upper()
        else:
            st.session_state.TICKERS_2[new_name] = new_ticker.upper()
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Odebrat existující")
all_current_stocks = {**st.session_state.TICKERS_1, **st.session_state.TICKERS_2}
stock_to_remove = st.sidebar.selectbox("Vyber akcii k odebrání", [""] + list(all_current_stocks.keys()))

if st.sidebar.button("❌ Odebrat akcii"):
    if stock_to_remove:
        if stock_to_remove in st.session_state.TICKERS_1:
            del st.session_state.TICKERS_1[stock_to_remove]
        elif stock_to_remove in st.session_state.TICKERS_2:
            del st.session_state.TICKERS_2[stock_to_remove]
        st.cache_data.clear()
        st.rerun()

# --- FUNKCE PRO NAČÍTÁNÍ DATA ---
@st.cache_data(ttl=60)
def get_portfolio_data(tickers_dict):
    data = []
    for name, ticker in tickers_dict.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            hist = hist.dropna(subset=['Close'])
            hist = hist[hist['Close'] > 0]
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                current = hist['Close'].iloc[-1]
                change_val = current - prev_close
                change_pct = (change_val / prev_close) * 100
            elif len(hist) == 1:
                prev_close = current = hist['Close'].iloc[0]
                change_val = 0.0
                change_pct = 0.0
            else:
                continue
            data.append({
                "Akcie": name, "Ticker": ticker, "Cena ($)": current,
                "Předchozí ($)": prev_close, "Změna (%)": change_pct, "Změna ($)": change_val
            })
        except Exception:
            continue
    return pd.DataFrame(data)

with st.spinner('Synchronizuji data z trhů...'):
    df1 = get_portfolio_data(st.session_state.TICKERS_1)
    df2 = get_portfolio_data(st.session_state.TICKERS_2)

# --- HLAVNÍ METRIKA ---
st.title("📈 Moje Investiční Portfolio")

if not df1.empty or not df2.empty:
    df_all = pd.concat([df1, df2], ignore_index=True)
    v_cur = df_all["Cena ($)"].sum()
    v_prev = df_all["Předchozí ($)"].sum()
    ch_val = v_cur - v_prev
    ch_pct = (ch_val / v_prev) * 100 if v_prev > 0 else 0
    
    st.metric(
        label="Denní nárůst portfolia (při držení 1 ks od každé pozice)",
        value=f"{v_cur:,.2f} USD",
        delta=f"{ch_val:,.2f} USD ({ch_pct:+.2f} %)"
    )

st.markdown("---")
st.markdown("### Přehled akcií")
sort_option = st.radio("Rychlé řazení:", ["Výchozí", "🚀 Růst", "📉 Pokles"], horizontal=True)

if sort_option == "🚀 Růst":
    if not df1.empty: df1 = df1.sort_values(by="Změna (%)", ascending=False)
    if not df2.empty: df2 = df2.sort_values(by="Změna (%)", ascending=False)
elif sort_option == "📉 Pokles":
    if not df1.empty: df1 = df1.sort_values(by="Změna (%)", ascending=True)
    if not df2.empty: df2 = df2.sort_values(by="Změna (%)", ascending=True)

col_tab1, col_tab2 = st.columns(2)

def style_df(df):
    display_df = df[["Akcie", "Cena ($)", "Změna (%)"]].copy()
    return display_df.style.map(
        lambda x: 'color: #00ff00; font-weight: 900' if x > 0 else ('color: #ff0000; font-weight: 900' if x < 0 else 'color: #ffffff; font-weight: 900'),
        subset=['Změna (%)']
    ).format({"Cena ($)": "{:.2f}", "Změna (%)": "{:+.2f} %"})

selected_ticker, selected_name = None, None

with col_tab1:
    st.write("**Tabulka 1: Růstové a Big Tech**")
    if not df1.empty:
        ev1 = st.dataframe(style_df(df1), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        if len(ev1.selection.rows) > 0:
            selected_ticker = df1.iloc[ev1.selection.rows[0]]["Ticker"]
            selected_name = df1.iloc[ev1.selection.rows[0]]["Akcie"]

with col_tab2:
    st.write("**Tabulka 2: Hodnotové a Ostatní**")
    if not df2.empty:
        ev2 = st.dataframe(style_df(df2), use_container_width=True, hide_
