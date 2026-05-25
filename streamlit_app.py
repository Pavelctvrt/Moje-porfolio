import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Moje Portfolio", layout="wide", initial_sidebar_state="collapsed")

# --- DEFINICE PORTFOLIA ---
# Převod tvých názvů na oficiální Yahoo Finance tickery
TICKERS_1 = {
    "SXR8.DE": "SXR8.DE", "Gold": "GLD", "Meta": "META", "Tesla": "TSLA", 
    "Netflix": "NFLX", "Google": "GOOGL", "Spotify": "SPOT", "Microsoft": "MSFT", 
    "Amazon": "AMZN", "Nvidia": "NVDA", "Arm": "ARM", "AMD": "AMD", 
    "Lam Research": "LRCX", "Applied Materials": "AMAT", "Super Micro": "SMCI", 
    "Palantir": "PLTR", "Alibaba": "BABA", "McDonalds": "MCD", "Novo Nordisk": "NVO", 
    "LVMH": "MC.PA", "CVS": "CVS", "Nike": "NKE", "Starbucks": "SBUX", 
    "GameStop": "GME", "Bitcoin": "BTC-USD", "Coinbase": "COIN", "Robinhood": "HOOD"
}

# CoreWeave a Circle odstraněny (soukromé firmy), LVT předpokládám jako Livento nebo překlep, zatím nechávám venku/příp. uprav.
TICKERS_2 = {
    "Pepsi": "PEP", "Coca Cola": "KO", "Realty Income": "O", "Pfizer": "PFE", 
    "JPMorgan": "JPM", "Uber": "UBER", "ČEZ": "CEZ.PR", "Broadcom": "AVGO", 
    "Micron": "MU", "SOFI": "SOFI", "Intel": "INTC", "QCOM": "QCOM", 
    "APP": "APP", "Serve Robotics": "SERV", "SPGI": "SPGI", "Dell": "DELL", 
    "UNH": "UNH"
}

ALL_TICKERS = {**TICKERS_1, **TICKERS_2}

# --- FUNKCE PRO NAČÍTÁNÍ DAT (S CACHE PRO RYCHLOST) ---
@st.cache_data(ttl=300) # Obnoví data každých 5 minut
def get_current_data(tickers_dict):
    data = []
    for name, ticker in tickers_dict.items():
        try:
            stock = yf.Ticker(ticker)
            # Získání dnešních dat pro výpočet změny
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[0]
                current = hist['Close'].iloc[1]
                change_pct = ((current - prev_close) / prev_close) * 100
            elif len(hist) == 1:
                current = hist['Close'].iloc[0]
                change_pct = 0.0
            else:
                continue
                
            data.append({
                "Název": name,
                "Ticker": ticker,
                "Cena": round(current, 2),
                "Změna (%)": round(change_pct, 2)
            })
        except Exception:
            continue
    return pd.DataFrame(data)

# --- NAČTENÍ DAT ---
with st.spinner('Načítám aktuální data z trhů (může trvat pár vteřin)...'):
    df1 = get_current_data(TICKERS_1)
    df2 = get_current_data(TICKERS_2)
    df_all = pd.concat([df1, df2], ignore_index=True) if not df1.empty and not df2.empty else pd.DataFrame()

# --- HLAVNÍ METRIKY ---
st.title("📈 Moje Investiční Portfolio")

if not df_all.empty:
    # Výpočty pro metriky
    best_stock = df_all.loc[df_all['Změna (%)'].idxmax()]
    avg_change = df_all['Změna (%)'].mean()
    total_positions = len(df_all)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="🚀 Nejvíce rostoucí akcie", 
                  value=f"{best_stock['Název']} ({best_stock['Ticker']})", 
                  delta=f"{best_stock['Změna (%)']}%")
    with col2:
        st.metric(label="📊 Průměrný denní pohyb", 
                  value=f"{avg_change:.2f} %", 
                  delta=f"{avg_change:.2f}%")
    with col3:
        st.metric(label="💼 Celkový počet pozic", value=total_positions)
else:
    st.warning("Nepodařilo se načíst data pro metriky.")

st.markdown("---")

# --- TABULKY ---
col_tab1, col_tab2 = st.columns(2)

def style_dataframe(df):
    return df.style.map(
        lambda x: 'color: green' if x > 0 else ('color: red' if x < 0 else ''),
        subset=['Změna (%)']
    ).format({"Změna (%)": "{:+.2f} %", "Cena": "{:.2f}"})

with col_tab1:
    st.subheader("Tabulka 1: Růstové a Big Tech")
    if not df1.empty:
        st.dataframe(style_dataframe(df1), use_container_width=True, hide_index=True)

with col_tab2:
    st.subheader("Tabulka 2: Hodnotové a Ostatní")
    if not df2.empty:
        st.dataframe(style_dataframe(df2), use_container_width=True, hide_index=True)

st.markdown("---")

# --- INTERAKTIVNÍ GRAF ---
st.subheader("📉 Detailní pohled na akcii")

# Výběr akcie a času
col_sel1, col_sel2 = st.columns([1, 1])
with col_sel1:
    # Vytvoření listu pro selectbox
    all_names = list(ALL_TICKERS.keys())
    selected_name = st.selectbox("Vyber akcii pro zobrazení grafu:", all_names)
    selected_ticker = ALL_TICKERS[selected_name]

with col_sel2:
    # Mapování časových úseků Yahoo Finance
    timeframes = {
        "1 Den": "1d", "1 Týden": "5d", "1 Měsíc": "1mo", "3 Měsíce": "3mo", 
        "Půl roku": "6mo", "Od začátku roku (YTD)": "ytd", "1 Rok": "1y", 
        "2 Roky": "2y", "5 Let": "5y", "Celá historie": "max"
    }
    selected_tf_label = st.selectbox("Vyber časový horizont:", list(timeframes.keys()), index=2) # Default 1 měsíc
    period = timeframes[selected_tf_label]

# Vykreslení grafu
if selected_ticker:
    interval = "1m" if period == "1d" else ("1d" if period in ["5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y"] else "1wk")
    
    with st.spinner('Načítám graf...'):
        history_data = yf.download(selected_ticker, period=period, interval=interval, progress=False)
        
        if not history_data.empty:
            # Převedení MultiIndexu (pokud ho yf.download vrátí)
            if isinstance(history_data.columns, pd.MultiIndex):
                history_data.columns = history_data.columns.droplevel(1)
                
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history_data.index, 
                y=history_data['Close'],
                mode='lines',
                name=selected_name,
                line=dict(color='#00ff00' if history_data['Close'].iloc[-1] >= history_data['Close'].iloc[0] else '#ff0000', width=2)
            ))
            
            fig.update_layout(
                title=f"Vývoj ceny {selected_name} ({selected_ticker}) - {selected_tf_label}",
                xaxis_title="Datum",
                yaxis_title="Cena",
                template="plotly_dark",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"Nepodařilo se stáhnout historická data pro {selected_name}.")
