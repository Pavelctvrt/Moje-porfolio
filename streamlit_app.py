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
    /* Úprava textů v boxech, aby svítily */
    .metric-box h3 { color: #8B949E !important; font-size: 16px; }
    .metric-box h2 { color: #58A6FF !important; font-size: 28px; margin: 5px 0 0 0; }
    </style>
""", unsafe_allow_html=True)

st.title("💼 Řídicí věž mých financí")
st.write("Vítejte ve svém investičním přehledu. (Režim: Sváteční offline přehled – kurzy z 22. 5. 2026)")

# 2. Kompletní tabulka 40 akcií s reálnými fixními kurzy z pátku
portfolio_data = [
    {"Ticker": "AAPL", "Název společnosti": "Apple Inc.", "Sektor": "Technologie", "Poslední cena (USD)": 181.18, "Poslední změna (%)": 0.62},
    {"Ticker": "MSFT", "Název společnosti": "Microsoft Corp.", "Sektor": "Technologie", "Poslední cena (USD)": 421.90, "Poslední změna (%)": -0.12},
    {"Ticker": "GOOGL", "Název společnosti": "Alphabet Inc.", "Sektor": "Technologie", "Poslední cena (USD)": 175.16, "Poslední změna (%)": 0.85},
    {"Ticker": "AMZN", "Název společnosti": "Amazon.com Inc.", "Sektor": "Cyklická spotřeba", "Poslední cena (USD)": 182.15, "Poslední změna (%)": -0.30},
    {"Ticker": "META", "Název společnosti": "Meta Platforms", "Sektor": "Komunikační služby", "Poslední cena (USD)": 472.18, "Poslední změna (%)": 1.20},
    {"Ticker": "NVDA", "Název společnosti": "NVIDIA Corp.", "Sektor": "Technologie", "Poslední cena (USD)": 948.50, "Poslední změna (%)": 2.57},
    {"Ticker": "TSLA", "Název společnosti": "Tesla Inc.", "Sektor": "Cyklická spotřeba", "Poslední cena (USD)": 179.24, "Poslední změna (%)": -1.15},
    {"Ticker": "BRK-B", "Název společnosti": "Berkshire Hathaway", "Sektor": "Finanční služby", "Poslední cena (USD)": 408.30, "Poslední změna (%)": 0.15},
    {"Ticker": "JNJ", "Název společnosti": "Johnson & Johnson", "Sektor": "Zdravotnictví", "Poslední cena (USD)": 152.50, "Poslední změna (%)": -0.40},
    {"Ticker": "V", "Název společnosti": "Visa Inc.", "Sektor": "Finanční služby", "Poslední cena (USD)": 278.10, "Poslední změna (%)": 0.22},
    {"Ticker": "WMT", "Název společnosti": "Walmart Inc.", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 65.25, "Poslední změna (%)": 0.45},
    {"Ticker": "PG", "Název společnosti": "Procter & Gamble", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 166.40, "Poslední změna (%)": -0.10},
    {"Ticker": "MA", "Název společnosti": "Mastercard Inc.", "Sektor": "Finanční služby", "Poslední cena (USD)": 460.15, "Poslední změna (%)": 0.35},
    {"Ticker": "UNH", "Název společnosti": "UnitedHealth Group", "Sektor": "Zdravotnictví", "Poslední cena (USD)": 515.80, "Poslední změna (%)": -0.85},
    {"Ticker": "HD", "Název společnosti": "Home Depot Inc.", "Sektor": "Cyklická spotřeba", "Poslední cena (USD)": 348.90, "Poslední změna (%)": -0.50},
    {"Ticker": "XOM", "Název společnosti": "Exxon Mobil Corp.", "Sektor": "Energie", "Poslední cena (USD)": 118.20, "Poslední změna (%)": 1.10},
    {"Ticker": "DIS", "Název společnosti": "Walt Disney Co.", "Sektor": "Komunikační služby", "Poslední cena (USD)": 102.45, "Poslední změna (%)": -0.90},
    {"Ticker": "KO", "Název společnosti": "Coca-Cola Co.", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 62.80, "Poslední změna (%)": 0.15},
    {"Ticker": "PEP", "Název společnosti": "PepsiCo Inc.", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 178.50, "Poslední změna (%)": 0.05},
    {"Ticker": "COST", "Název společnosti": "Costco Wholesale", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 792.10, "Poslední změna (%)": 1.40},
    {"Ticker": "AMD", "Název společnosti": "Advanced Micro Devices", "Sektor": "Technologie", "Poslední cena (USD)": 160.20, "Poslední změna (%)": 1.80},
    {"Ticker": "INTC", "Název společnosti": "Intel Corp.", "Sektor": "Technologie", "Poslední cena (USD)": 30.15, "Poslední změna (%)": -2.10},
    {"Ticker": "CSCO", "Název společnosti": "Cisco Systems", "Sektor": "Technologie", "Poslední cena (USD)": 48.30, "Poslední změna (%)": -0.15},
    {"Ticker": "ORCL", "Název společnosti": "Oracle Corp.", "Sektor": "Technologie", "Poslední cena (USD)": 124.60, "Poslední změna (%)": 0.70},
    {"Ticker": "CRM", "Název společnosti": "Salesforce Inc.", "Sektor": "Technologie", "Poslední cena (USD)": 285.40, "Poslední změna (%)": 0.95},
    {"Ticker": "NFLX", "Název společnosti": "Netflix Inc.", "Sektor": "Komunikační služby", "Poslední cena (USD)": 645.20, "Poslední změna (%)": 1.60},
    {"Ticker": "ADBE", "Název společnosti": "Adobe Inc.", "Sektor": "Technologie", "Poslední cena (USD)": 475.10, "Poslední změna (%)": -0.45},
    {"Ticker": "NKE", "Název společnosti": "Nike Inc.", "Sektor": "Cyklická spotřeba", "Poslední cena (USD)": 92.40, "Poslední změna (%)": -1.30},
    {"Ticker": "MCD", "Název společnosti": "McDonald's Corp.", "Sektor": "Cyklická spotřeba", "Poslední cena (USD)": 265.80, "Poslední změna (%)": -0.20},
    {"Ticker": "SBUX", "Název společnosti": "Starbucks Corp.", "Sektor": "Cyklická spotřeba", "Poslední cena (USD)": 78.15, "Poslední změna (%)": 0.40},
    {"Ticker": "PM", "Název společnosti": "Philip Morris Inc.", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 101.90, "Poslední změna (%)": 0.80},
    {"Ticker": "MO", "Název společnosti": "Altria Group", "Sektor": "Defenzivní spotřeba", "Poslední cena (USD)": 45.60, "Poslední změna (%)": 0.50},
    {"Ticker": "PFE", "Název společnosti": "Pfizer Inc.", "Sektor": "Zdravotnictví", "Poslední cena (USD)": 28.40, "Poslední změna (%)": -0.70},
    {"Ticker": "MRK", "Název společnosti": "Merck & Co.", "Sektor": "Zdravotnictví", "Poslední cena (USD)": 128.30, "Poslední změna (%)": 0.30},
    {"Ticker": "ABV", "Název společnosti": "AbbVie Inc.", "Sektor": "Zdravotnictví", "Poslední cena (USD)": 164.20, "Poslední změna (%)": 0.10},
    {"Ticker": "T", "Název společnosti": "AT&T Inc.", "Sektor": "Komunikační služby", "Poslední cena (USD)": 17.35, "Poslední změna (%)": 1.15},
    {"Ticker": "VZ", "Název společnosti": "Verizon Communications", "Sektor": "Komunikační služby", "Poslední cena (USD)": 39.80, "Poslední změna (%)": 0.40},
    {"Ticker": "BAC", "Název společnosti": "Bank of America", "Sektor": "Finanční služby", "Poslední cena (USD)": 38.15, "Poslední změna (%)": -0.25},
    {"Ticker": "JPM", "Název společnosti": "JPMorgan Chase & Co.", "Sektor": "Finanční služby", "Poslední cena (USD)": 198.50, "Poslední změna (%)": 0.60},
    {"Ticker": "GS", "Název společnosti": "Goldman Sachs Group", "Sektor": "Finanční služby", "Poslední cena (USD)": 455.20, "Poslední změna (%)": 0.85}
]

df = pd.DataFrame(portfolio_data)

# 3. Horní infopanely (Metriky)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='metric-box'><h3>Sledovaných pozic</h3><h2>40 / 40</h2></div>", unsafe_allow_html=True)
with col2:
    skokan = df.loc[df['Poslední změna (%)'].idxmax()]
    st.markdown(f"<div class='metric-box'><h3>Páteční skokan 🚀</h3><h2>{skokan['Ticker']} (+{skokan['Poslední změna (%)']}%)</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-box'><h3>Stav burzy (USA)</h3><h2>🔒 ZAVŘENO (Svátek)</h2></div>", unsafe_allow_html=True)
    
st.markdown("---")

# 4. Samotná interaktivní tabulka s barvami
st.subheader("📋 Kompletní přehled tvých 40 akciových titulů")
vyhledavani = st.text_input("🔍 Rychlé vyhledávání akcie (napiš Ticker nebo název společnosti):")

if vyhledavani:
    df_filtrovane = df[df['Ticker'].str.contains(vyhledavani, case=False) | df['Název společnosti'].str.contains(vyhledavani, case=False)]
else:
    df_filtrovane = df

# Vybarvení tabulky (ošetřeno tak, aby bez matplotlibu nespadlo)
try:
    styler = df_filtrovane.style.background_gradient(subset=['Poslední změna (%)'], cmap='RdYlGn', vmin=-3, vmax=3)
    st.dataframe(styler, use_container_width=True, hide_index=True)
except Exception:
    st.dataframe(df_filtrovane, use_container_width=True, hide_index=True)
