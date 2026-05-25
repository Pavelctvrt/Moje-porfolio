import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 1. Nastavení stránky
st.set_page_config(page_title="Moje Portfolio", layout="wide", initial_sidebar_state="expanded")

# Stylizace aplikace pomocí CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .metric-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Řídicí věž mých financí")
st.write("Vítejte ve svém investičním přehledu. Data jsou automaticky stahována live z Yahoo Finance.")

# 2. Definice tvých 40 akcií (Tickery)
# Seznam obsahuje mix populárních amerických, evropských i globálních titulů
tickery = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BRK-B", "JNJ", "V",
    "WMT", "PG", "MA", "UNH", "HD", "XOM", "DIS", "KO", "PEP", "COST",
    "AMD", "INTC", "CSCO", "ORCL", "CRM", "NFLX", "ADBE", "NKE", "MCD", "SBUX",
    "PM", "MO", "PFE", "MRK", "ABV", "T", "VZ", "BAC", "JPM", "GS"
]

# 3. Načítání dat z Yahoo Finance
@st.cache_data(ttl=3600)  # Data se uloží do paměti na 1 hodinu, aby web běžel bleskově
def nacti_data_portfolia(seznam_tickeru):
    data_list = []
    progres_bar = st.progress(0, text="Stahuji aktuální kurzy z burzy...")
    
    for i, tkr in enumerate(seznam_tickeru):
        try:
            akcie = yf.Ticker(tkr)
            info = akcie.info
            historie = akcie.history(period="5d")
            
            if not historie.empty:
                aktualni_cena = historie['Close'].iloc[-1]
                predchozi_cena = historie['Close'].iloc[-2] if len(historie) > 1 else aktualni_cena
                zmena_procenta = ((aktualni_cena - pred
