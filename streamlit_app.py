import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Moje Portfolio", layout="wide", initial_sidebar_state="expanded")

# --- VYNUCENÍ ČERNÉHO POZADÍ A MAXIMÁLNÍ ČITELNOSTI ---
st.markdown("""
<style>
    /* Základní pozadí */
    .stApp, .main, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Vynucení čistě bílého a tučnějšího písma pro lepší čitelnost na slunci */
    .stMarkdown p, .stText, label, .stMetricLabel, [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Zvětšení metrik */
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
    }
    
    /* Tabulky */
    [data-testid="stDataFrame"] {
        background-color: #111111 !important;
    }
    
    /* Schování zbytečností */
    footer {visibility: hidden;}
    header {background: transparent !important;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACE PORTFOLIA DO PAMĚTI (SESSION STATE) ---
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
        "APP":
