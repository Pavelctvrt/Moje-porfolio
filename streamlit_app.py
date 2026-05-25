import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Moje Portfolio", layout="wide")
st.title("💼 Řídicí věž mých financí")

test_tickery = ["AAPL", "MSFT", "GOOGL"]
st.write("Načítám testovací data z Yahoo Finance...")

for tkr in test_tickery:
    try:
        akcie = yf.Ticker(tkr)
        historie = akcie.history(period="1mo")
        if not historie.empty:
            aktualni_cena = historie['Close'].iloc[-1]
            st.write(f"✅ **{tkr}**: {aktualni_cena:.2f} USD")
    except Exception as e:
        st.write(f"Chyba u {tkr}: {e}")
