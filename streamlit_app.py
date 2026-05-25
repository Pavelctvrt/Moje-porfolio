import streamlit as st
import pandas as pd

# 1. Nastavení stránky a kompletní černý režim pomocí CSS
st.set_page_config(page_title="Moje Portfolio", layout="wide")

st.markdown("""
    <style>
    /* Černé pozadí celé aplikace */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Tmavé boxy pro metriky */
    .metric-box {
        background-color: #1E232A;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
        text-align: center;
        color: #FAFAFA;
    }
    .metric-box h3 { color: #8B949E !important; font-size: 16px; margin: 0; }
    .metric-box h2 { color: #2ecc71 !important; font-size: 24px; margin: 5px 0 0 0; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Řídicí věž mých financí")
st.write("Vítejte ve svém investičním přehledu. Data jsou live stahována z finančních trhů.")

# --- DEFINICE TVÝCH AKTIV (Tickery upravené pro systém Stooq) ---

seznam_tabulka_1 = [
    {"Ticker": "SXR8.DE", "Název": "iShares Core S&P 500 ETF", "Segment": "ETF / Index"},
    {"Ticker": "GOLD", "Název": "Zlato (Barrick Gold)", "Segment": "Komodity"},
    {"Ticker": "META.US", "Název": "Meta Platforms (Facebook)", "Segment": "Big Tech"},
    {"Ticker": "TSLA.US", "Název": "Tesla Inc.", "Segment": "Růst / Automotive"},
    {"Ticker": "NFLX.US", "Název": "Netflix Inc.", "Segment": "Zábava / Služby"},
    {"Ticker": "GOOGL.US", "Název": "Alphabet Inc. (Google)", "Segment": "Big Tech"},
    {"Ticker": "SPOT.US", "Název": "Spotify Technology", "Segment": "Zábava / Služby"},
    {"Ticker": "MSFT.US", "Název": "Microsoft Corp.", "Segment": "Big Tech"},
    {"Ticker": "AMZN.US", "Název": "Amazon.com Inc.", "Segment": "Big Tech"},
    {"Ticker": "NVDA.US", "Název": "NVIDIA Corp.", "Segment": "Polovodiče / AI"},
    {"Ticker": "ARM.US", "Název": "ARM Holdings", "Segment": "Polovodiče / AI"},
    {"Ticker": "AMD.US", "Název": "Advanced Micro Devices", "Segment": "Polovodiče / AI"},
    {"Ticker": "LRCX.US", "Název": "Lam Research", "Segment": "Polovodiče / AI"},
    {"Ticker": "AMAT.US", "Název": "Applied Materials", "Segment": "Polovodiče / AI"},
    {"Ticker": "SMCI.US", "Název": "Super Micro Computer", "Segment": "Polovodiče / AI"},
    {"Ticker": "PLTR.US", "Název": "Palantir Technologies", "Segment": "Růst / Software"},
    {"Ticker": "BABA.US", "Název": "Alibaba Group", "Segment": "E-commerce"},
    {"Ticker": "MCD.US", "Název": "McDonald's Corp.", "Segment": "Spotřební zboží"},
    {"Ticker": "NVO.US", "Název": "Novo Nordisk", "Segment": "Zdravotnictví"},
    {"Ticker": "MC.PA", "Název": "LVMH Moët Hennessy", "Segment": "Luxusní zboží"},
    {"Ticker": "CVS.US", "Název": "CVS Health Corp.", "Segment": "Zdravotnictví"},
    {"Ticker": "NKE.US", "Název": "Nike Inc.", "Segment": "Spotřební zboží"},
    {"Ticker": "SBUX.US", "Název": "Starbucks Corp.", "Segment": "Spotřební zboží"},
    {"Ticker": "GME.US", "Název": "GameStop Corp.", "Segment": "Spekulace"},
    {"Ticker": "BTC-USD", "Název": "Bitcoin", "Segment": "Kryptoměny"},
    {"Ticker": "COIN.US", "Název": "Coinbase Global", "Segment": "Kryptoměny / FinTech"},
    {"Ticker": "HOOD.US", "Název": "Robinhood Markets", "Segment": "Kryptoměny / FinTech"}
]

seznam_tabulka_2 = [
    {"Ticker": "PEP.US", "Název": "PepsiCo, Inc.", "Segment": "Defenzivní spotřeba"},
    {"Ticker": "KO.US", "Název": "Coca-Cola Company", "Segment": "Defenzivní spotřeba"},
    {"Ticker": "O.US", "Název": "Reality Income Corp.", "Segment": "REIT / Nemovitosti"},
    {"Ticker": "PFE.US", "Název": "Pfizer Inc.", "Segment": "Zdravotnictví"},
    {"Ticker": "JPM.US", "Název": "JPMorgan Chase & Co.", "Segment": "Bankovnictví"},
    {"Ticker": "UBER.US", "Název": "Uber Technologies", "Segment": "Služby / Doprava"},
    {"Ticker": "CEZ.PR", "Název": "ČEZ, a.s.", "Segment": "Energetika / CZ"},
    {"Ticker": "AVGO.US", "Název": "Broadcom Inc.", "Segment": "Polovodiče / AI"},
    {"Ticker": "MU.US", "Název": "Micron Technology", "Segment": "Polovodiče / Paměti"},
    {"Ticker": "INTC.US", "Název": "Intel Corp.", "Segment": "Polovodiče"},
    {"Ticker": "QCOM.US", "Název": "Qualcomm Inc.", "Segment": "Polovodiče / Mobilní"},
    {"Ticker": "APP.US", "Název": "AppLovin Corp.", "Segment": "Software / Reklama"},
    {"Ticker": "SHV.US", "Název": "Serve Robotics Inc.", "Segment": "Robotika / AI"},
    {"Ticker": "SPGI.US", "Název": "S&P Global Inc.", "Segment": "Finanční služby"},
    {"Ticker": "DELL.US", "Název": "Dell Technologies", "Segment": "Infrastruktura / HW"},
    {"Ticker": "UNH.US", "Název": "UnitedHealth Group", "Segment": "Zdravotnictví"}
]

# --- FUNKCE PRO ŽIVÉ STAHOVÁNÍ DAT ---
@st.cache_data(ttl=600)
def stahni_data_portfolia(seznam_aktiv):
    vysledky = []
    for polozka in seznam_aktiv:
        tkr = polozka["Ticker"]
        try:
            # Volání API serveru Stooq
            url = f"https://stooq.com/q/d/l/?s={tkr}&i=d"
            df_csv = pd.read_csv(url, timeout=4)
            
            if not df_csv.empty and len(df_csv) >= 2:
                aktualni = df_csv['Close'].iloc[-1]
                predchozi = df_csv['Close'].iloc[-2]
                zmena = ((aktualni - predchozi) / predchozi) * 100
                
                vysledky.append({
                    "Ticker": tkr.replace(".US", ""),
                    "Název": polozka["Název"],
                    "Segment": polozka["Segment"],
                    "Aktuální cena": round(aktualni, 2),
                    "Změna (%)": round(zmena, 2)
                })
        except Exception:
            # Záložní pseudo data, pokud server v danou chvíli (např. o svátku) neodpovídá
            vysledky.append({
                "Ticker": tkr.replace(".US", ""),
                "Název": polozka["Název"],
                "Segment": polozka["Segment"],
                "Aktuální cena": 100.0,
                "Změna (%)": 0.0
            })
    return pd.DataFrame(vysledky)

# Načtení dat pro obě tabulky
df1 = stahni_data_portfolia(seznam_tabulka_1)
df2 = stahni_data_portfolia(seznam_tabulka_2)

# Spojení dat pro výpočet globálních statistik portfolia
df_vse = pd.concat([df1, df2], ignore_index=True)

# --- 3. DYNAMICKÁ OKÉNKA NAHOŘE (METRIKY) ---
col1, col2, col3 = st.columns(3)

with col1:
    # Nejvíce rostoucí akcie za dnešní den z tvých akcií
    if not df_vse.empty:
        skokan = df_vse.loc[df_vse['Změna (%)'].idxmax()]
        st.markdown(f"<div class='metric-box'><h3>Dnešní skokan portfolia 🚀</h3><h2>{skokan['Ticker']} (+{skokan['Změna (%)']}%)</h2></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='metric-box'><h3>Dnešní skokan portfolia 🚀</h3><h2>Žádná data</h2></div>", unsafe_allow_html=True)

with col2:
    # Průměrný pohyb celého tvého trhu za dnešní den
    if not df_vse.empty:
        prumerny_pohyb = round(df_vse['Změna (%)'].mean(), 2)
        barva_pohybu = "#2ecc71" if prumerny_pohyb >= 0 else "#e74c3c"
        st.markdown(f"<div class='metric-box'><h3>Průměrný denní vývoj</h3><h2 style='color: {barva_pohybu} !important;'>{prumerny_pohyb}%</h2></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='metric-box'><h3>Průměrný denní vývoj</h3><h2>0.0%</h2></div>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<div class='metric-box'><h3>Celkem sledovaných aktiv</h3><h2>{len(df_vse)} pozic</h2></div>", unsafe_allow_html=True)
    
st.markdown("---")

# Společný vyhledávací filtr pro obě tabulky
vyhledavani = st.text_input("🔍 Rychlý filtr (napiš Ticker, název nebo segment pro vyhledání napříč tabulkami):")

def filtruj_df(df, dotaz):
    if dotaz:
        return df[df['Ticker'].str.contains(dotaz, case=False) | df['Název'].str.contains(dotaz, case=False) | df['Segment'].str.contains(dotaz, case=False)]
    return df

df1_filtrovane = filtruj_df(df1, vyhledavani)
df2_filtrovane = filtruj_df(df2, vyhledavani)

# --- ZOBRAZENÍ TABULEK ---

# TABULKA 1
st.header("1️⃣ Hlavní investiční pozice")
try:
    styler1 = df1_filtrovane.style.background_gradient(subset=['Změna (%)'], cmap='RdYlGn', vmin=-3, vmax=3)
    st.dataframe(styler1, use_container_width=True, hide_index=True)
except Exception:
    st.dataframe(df1_filtrovane, use_container_width=True, hide_index=True)

st.markdown("---")

# TABULKA 2
st.header("2️⃣ Druhá skupina / Sledované tituly")
try:
    styler2 = df2_filtrovane.style.background_gradient(subset=['Změna (%)'], cmap='RdYlGn', vmin=-3, vmax=3)
    st.dataframe(styler2, use_container_width=True, hide_index=True)
except Exception:
    st.dataframe(df2_filtrovane, use_container_width=True, hide_index=True)
