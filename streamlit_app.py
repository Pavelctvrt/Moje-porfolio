import streamlit as st
import pandas as pd

# 1. Nastavení stránky
st.set_page_config(page_title="Moje Portfolio", layout="wide")

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
st.write("Vítejte ve svém investičním přehledu. Dnes je v USA svátek, zobrazujeme poslední uzavřené kurzy.")

# Kompletní seznam 40 akcií
akcie_data = [
    {"Ticker": "AAPL", "Název": "Apple Inc.", "Sektor": "Technologie"},
    {"Ticker": "MSFT", "Název": "Microsoft Corp.", "Sektor": "Technologie"},
    {"Ticker": "GOOGL", "Název": "Alphabet Inc.", "Sektor": "Technologie"},
    {"Ticker": "AMZN", "Název": "Amazon.com Inc.", "Sektor": "Cyklická spotřeba"},
    {"Ticker": "META", "Název": "Meta Platforms", "Sektor": "Komunikační služby"},
    {"Ticker": "NVDA", "Název": "NVIDIA Corp.", "Sektor": "Technologie"},
    {"Ticker": "TSLA", "Název": "Tesla Inc.", "Sektor": "Cyklická spotřeba"},
    {"Ticker": "BRK-B", "Název": "Berkshire Hathaway", "Sektor": "Finanční služby"},
    {"Ticker": "JNJ", "Název": "Johnson & Johnson", "Sektor": "Zdravotnictví"},
    {"Ticker": "V", "Název": "Visa Inc.", "Sektor": "Finanční služby"},
    {"Ticker": "WMT", "Název": "Walmart Inc.", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "PG", "Název": "Procter & Gamble", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "MA", "Název": "Mastercard Inc.", "Sektor": "Finanční služby"},
    {"Ticker": "UNH", "Název": "UnitedHealth Group", "Sektor": "Zdravotnictví"},
    {"Ticker": "HD", "Název": "Home Depot Inc.", "Sektor": "Cyklická spotřeba"},
    {"Ticker": "XOM", "Název": "Exxon Mobil Corp.", "Sektor": "Energie"},
    {"Ticker": "DIS", "Název": "Walt Disney Co.", "Sektor": "Komunikační služby"},
    {"Ticker": "KO", "Název": "Coca-Cola Co.", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "PEP", "Název": "PepsiCo Inc.", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "COST", "Název": "Costco Wholesale", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "AMD", "Název": "Advanced Micro Devices", "Sektor": "Technologie"},
    {"Ticker": "INTC", "Název": "Intel Corp.", "Sektor": "Technologie"},
    {"Ticker": "CSCO", "Název": "Cisco Systems", "Sektor": "Technologie"},
    {"Ticker": "ORCL", "Název": "Oracle Corp.", "Sektor": "Technologie"},
    {"Ticker": "CRM", "Název": "Salesforce Inc.", "Sektor": "Technologie"},
    {"Ticker": "NFLX", "Název": "Netflix Inc.", "Sektor": "Komunikační služby"},
    {"Ticker": "ADBE", "Název": "Adobe Inc.", "Sektor": "Technologie"},
    {"Ticker": "NKE", "Název": "Nike Inc.", "Sektor": "Cyklická spotřeba"},
    {"Ticker": "MCD", "Název": "McDonald's Corp.", "Sektor": "Cyklická spotřeba"},
    {"Ticker": "SBUX", "Název": "Starbucks Corp.", "Sektor": "Cyklická spotřeba"},
    {"Ticker": "PM", "Název": "Philip Morris Inc.", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "MO", "Název": "Altria Group", "Sektor": "Defenzivní spotřeba"},
    {"Ticker": "PFE", "Název": "Pfizer Inc.", "Sektor": "Zdravotnictví"},
    {"Ticker": "MRK", "Název": "Merck & Co.", "Sektor": "Zdravotnictví"},
    {"Ticker": "ABV", "Název": "AbbVie Inc.", "Sektor": "Zdravotnictví"},
    {"Ticker": "T", "Název": "AT&T Inc.", "Sektor": "Komunikační služby"},
    {"Ticker": "VZ", "Název": "Verizon Communications", "Sektor": "Komunikační služby"},
    {"Ticker": "BAC", "Název": "Bank of America", "Sektor": "Finanční služby"},
    {"Ticker": "JPM", "Název": "JPMorgan Chase & Co.", "Sektor": "Finanční služby"},
    {"Ticker": "GS", "Název": "Goldman Sachs Group", "Sektor": "Finanční služby"}
]

@st.cache_data(ttl=3600)
def stahni_data_svatek():
    vysledky = []
    for položka in akcie_data:
        tkr = položka["Ticker"]
        stooq_tkr = tkr.replace("-", ".").upper() + ".US"
        try:
            # Přidáme timeout=5, aby se kód u žádné akcie nezasekl, když neodpovídá
            url = f"https://stooq.com/q/d/l/?s={stooq_tkr}&i=d"
            df_csv = pd.read_csv(url, timeout=5)
            
            if not df_csv.empty and len(df_csv) >= 2:
                # Vezmeme poslední dva dostupné dny v historii (patek a ctvrtek)
                aktualni = df_csv['Close'].iloc[-1]
                predchozi = df_csv['Close'].iloc[-2]
                zmena = ((aktualni - predchozi) / predchozi) * 100
                
                vysledky.append({
                    "Ticker": tkr,
                    "Název společnosti": položka["Název"],
                    "Sektor": položka["Sektor"],
                    "Poslední cena (USD)": round(aktualni, 2),
                    "Poslední změna (%)": round(zmena, 2)
                })
        except Exception:
            pass
    return pd.DataFrame(vysledky)

df = stahni_data_svatek()

if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box'><h3>Sledovaných pozic</h3><h2>{len(df)} / 40</h2></div>", unsafe_allow_html=True)
    with col2:
        skokan = df.loc[df['Poslední změna (%)'].idxmax()]
        st.markdown(f"<div class='metric-box'><h3>Poslední skokan 🚀</h3><h2>{skokan['Ticker']} ({skokan['Poslední změna (%)']}%)</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-box'><h3>Stav trhů</h3><h2>🔒 USA Svátek</h2></div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    st.subheader("📋 Přehled portfolia (Data z posledního obchodního dne)")
    vyhledavani = st.text_input("🔍 Rychlé vyhledávání akcie:")
    
    if vyhledavani:
        df_filtrovane = df[df['Ticker'].str.contains(vyhledavani, case=False) | df['Název společnosti'].str.contains(vyhledavani, case=False)]
    else:
        df_filtrovane = df
        
    st.dataframe(
        df_filtrovane.style.background_gradient(subset=['Poslední změna (%)'], cmap='RdYlGn', vmin=-3, vmax=3),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Systém Stooq dnes kvůli svátku neodpovídá. Zkuste to prosím znovu za chvíli tlačítkem níže.")
    if st.button("🔄 Načíst znovu"):
        st.cache_data.clear()
        st.rerun()
