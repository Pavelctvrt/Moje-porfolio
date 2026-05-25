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
    .metric-box h3 { color: #8B949E !important; font-size: 16px; }
    .metric-box h2 { color: #2ecc71 !important; font-size: 28px; margin: 5px 0 0 0; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Řídicí věž mých financí")
st.write("Vítejte ve svém investičním přehledu. (Režim: Sváteční offline přehled – kurzy z 22. 5. 2026)")

# --- DEFINICE DATASETŮ PRO OBĚ TABULKY ---

# Tabulka 1: Co vlastním / Hlavní seznam
data_tabulka_1 = [
    {"Ticker": "SXR8.DE", "Název": "iShares Core S&P 500 ETF", "Segment": "ETF / Index", "Cena": 512.40, "Změna (%)": 0.35},
    {"Ticker": "GOLD", "Název": "Zlato (Barrick Gold)", "Segment": "Komodity", "Cena": 17.15, "Změna (%)": -0.20},
    {"Ticker": "META", "Název": "Meta Platforms (Facebook)", "Segment": "Big Tech", "Cena": 472.18, "Změna (%)": 1.20},
    {"Ticker": "TSLA", "Název": "Tesla Inc.", "Segment": "Růst / Automotive", "Cena": 179.24, "Změna (%)": -1.15},
    {"Ticker": "NFLX", "Název": "Netflix Inc.", "Segment": "Zábava / Služby", "Cena": 645.20, "Změna (%)": 1.60},
    {"Ticker": "GOOGL", "Název": "Alphabet Inc. (Google)", "Segment": "Big Tech", "Cena": 175.16, "Změna (%)": 0.85},
    {"Ticker": "SPOT", "Název": "Spotify Technology", "Segment": "Zábava / Služby", "Cena": 295.10, "Změna (%)": 2.10},
    {"Ticker": "MSFT", "Název": "Microsoft Corp.", "Segment": "Big Tech", "Cena": 421.90, "Změna (%)": -0.12},
    {"Ticker": "AMZN", "Název": "Amazon.com Inc.", "Segment": "Big Tech", "Cena": 182.15, "Změna (%)": -0.30},
    {"Ticker": "NVDA", "Název": "NVIDIA Corp.", "Segment": "Polovodiče / AI", "Cena": 948.50, "Změna (%)": 2.57},
    {"Ticker": "ARM", "Název": "ARM Holdings", "Segment": "Polovodiče / AI", "Cena": 122.40, "Změna (%)": 1.10},
    {"Ticker": "AMD", "Název": "Advanced Micro Devices", "Segment": "Polovodiče / AI", "Cena": 160.20, "Změna (%)": 1.80},
    {"Ticker": "LRCX", "Název": "Lam Research", "Segment": "Polovodiče / AI", "Cena": 932.10, "Změna (%)": 0.95},
    {"Ticker": "AMAT", "Název": "Applied Materials", "Segment": "Polovodiče / AI", "Cena": 214.50, "Změna (%)": 1.40},
    {"Ticker": "SMCI", "Název": "Super Micro Computer", "Segment": "Polovodiče / AI", "Cena": 825.30, "Změna (%)": -3.40},
    {"Ticker": "PLTR", "Název": "Palantir Technologies", "Segment": "Růst / Software", "Cena": 21.45, "Změna (%)": 0.75},
    {"Ticker": "BABA", "Název": "Alibaba Group", "Segment": "E-commerce", "Cena": 82.30, "Změna (%)": -0.55},
    {"Ticker": "MCD", "Název": "McDonald's Corp.", "Segment": "Spotřební zboží", "Cena": 265.80, "Změna (%)": -0.20},
    {"Ticker": "NVO", "Název": "Novo Nordisk", "Segment": "Zdravotnictví", "Cena": 128.40, "Změna (%)": 0.90},
    {"Ticker": "MC.PA", "Název": "LVMH Moët Hennessy", "Segment": "Luxusní zboží", "Cena": 745.00, "Změna (%)": -0.40},
    {"Ticker": "CVS", "Název": "CVS Health Corp.", "Segment": "Zdravotnictví", "Cena": 56.10, "Změna (%)": -1.05},
    {"Ticker": "NKE", "Název": "Nike Inc.", "Segment": "Spotřební zboží", "Cena": 92.40, "Změna (%)": -1.30},
    {"Ticker": "SBUX", "Název": "Starbucks Corp.", "Segment": "Spotřební zboží", "Cena": 78.15, "Změna (%)": 0.40},
    {"Ticker": "GME", "Název": "GameStop Corp.", "Segment": "Spekulace", "Cena": 19.00, "Změna (%)": -5.20},
    {"Ticker": "BTC-USD", "Název": "Bitcoin", "Segment": "Kryptoměny", "Cena": 67250.00, "Změna (%)": 1.15},
    {"Ticker": "COIN", "Název": "Coinbase Global", "Segment": "Kryptoměny / FinTech", "Cena": 222.40, "Změna (%)": 3.80},
    {"Ticker": "HOOD", "Název": "Robinhood Markets", "Segment": "Kryptoměny / FinTech", "Cena": 19.10, "Změna (%)": 1.45}
]

# Tabulka 2: Druhá skupina / Sledované pozice (Watchlist)
data_tabulka_2 = [
    {"Ticker": "PEP", "Název": "PepsiCo, Inc.", "Segment": "Defenzivní spotřeba", "Cena": 178.50, "Změna (%)": 0.05},
    {"Ticker": "KO", "Název": "Coca-Cola Company", "Segment": "Defenzivní spotřeba", "Cena": 62.80, "Změna (%)": 0.15},
    {"Ticker": "O", "Název": "Reality Income Corp.", "Segment": "REIT / Nemovitosti", "Cena": 54.30, "Změna (%)": -0.10},
    {"Ticker": "PFE", "Název": "Pfizer Inc.", "Segment": "Zdravotnictví", "Cena": 28.40, "Změna (%)": -0.70},
    {"Ticker": "JPM", "Název": "JPMorgan Chase & Co.", "Segment": "Bankovnictví", "Cena": 198.50, "Změna (%)": 0.60},
    {"Ticker": "UBER", "Název": "Uber Technologies", "Segment": "Služby / Doprava", "Cena": 68.20, "Změna (%)": 1.40},
    {"Ticker": "CEZ.PR", "Název": "ČEZ, a.s.", "Segment": "Energetika / CZ", "Cena": 942.00, "Změna (%)": 0.25},
    {"Ticker": "AVGO", "Název": "Broadcom Inc.", "Segment": "Polovodiče / AI", "Cena": 1395.00, "Změna (%)": 0.65},
    {"Ticker": "MU", "Název": "Micron Technology", "Segment": "Polovodiče / Paměti", "Cena": 125.40, "Změna (%)": 2.10},
    {"Ticker": "CORE", "Název": "CoreWeave (Privátní/Sledované)", "Segment": "AI Cloud / Infrastruktura", "Cena": 100.00, "Změna (%)": 0.00},
    {"Ticker": "CRCL", "Název": "Circle (USDC)", "Segment": "FinTech / Crypto", "Cena": 1.00, "Změna (%)": 0.00},
    {"Ticker": "SOFI", "Název": "SoFi Technologies", "Segment": "FinTech / Banky", "Cena": 6.85, "Změna (%)": -1.20},
    {"Ticker": "INTC", "Název": "Intel Corp.", "Segment": "Polovodiče", "Cena": 30.15, "Změna (%)": -2.10},
    {"Ticker": "QCOM", "Název": "Qualcomm Inc.", "Segment": "Polovodiče / Mobilní", "Cena": 185.30, "Změna (%)": 1.15},
    {"Ticker": "APP", "Název": "AppLovin Corp.", "Segment": "Software / Reklama", "Cena": 82.40, "Změna (%)": 3.45},
    {"Ticker": "SHV", "Název": "Serve Robotics Inc.", "Segment": "Robotika / AI", "Cena": 2.80, "Změna (%)": -4.10},
    {"Ticker": "SPGI", "Název": "S&P Global Inc.", "Segment": "Finanční služby", "Cena": 435.10, "Změna (%)": 0.50},
    {"Ticker": "DELL", "Název": "Dell Technologies", "Segment": "Infrastruktura / HW", "Cena": 132.60, "Změna (%)": 2.80},
    {"Ticker": "UNH", "Název": "UnitedHealth Group", "Segment": "Zdravotnictví", "Cena": 515.80, "Změna (%)": -0.85},
    {"Ticker": "LVT", "Název": "LVT (Sledovaný titul)", "Segment": "Ostatní / Růst", "Cena": 15.40, "Změna (%)": 0.00}
]

df1 = pd.DataFrame(data_tabulka_1)
df2 = pd.DataFrame(data_tabulka_2)

# 3. Horní infopanely (Metriky)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='metric-box'><h3>Tabulka 1 (Základní)</h3><h2>{len(df1)} pozic</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'><h3>Tabulka 2 (Sledované)</h3><h2>{len(df2)} pozic</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-box'><h3>Celkový přehled</h3><h2>🖤 Černý režim</h2></div>", unsafe_allow_html=True)
    
st.markdown("---")

# Společný vyhledávací filtr
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
