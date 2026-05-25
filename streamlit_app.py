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
tickery = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BRK-B", "JNJ", "V",
    "WMT", "PG", "MA", "UNH", "HD", "XOM", "DIS", "KO", "PEP", "COST",
    "AMD", "INTC", "CSCO", "ORCL", "CRM", "NFLX", "ADBE", "NKE", "MCD", "SBUX",
    "PM", "MO", "PFE", "MRK", "ABV", "T", "VZ", "BAC", "JPM", "GS"
]

# 3. Načítání dat z Yahoo Finance
@st.cache_data(ttl=3600)
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
                if len(historie) > 1:
                    predchozi_cena = historie['Close'].iloc[-2]
                else:
                    predchozi_cena = aktualni_cena
                
                zmena_procenta = ((aktualni_cena - predchozi_cena) / predchozi_cena) * 100
                
                nazev = info.get('longName', tkr)
                sektor = info.get('sector', 'Neznámý sektor')
                mena = info.get('currency', 'USD')
                
                data_list.append({
                    "Ticker": tkr,
                    "Název společnosti": nazev,
                    "Sektor": sektor,
                    "Aktuální cena": round(aktualni_cena, 2),
                    "Denní změna (%)": round(zmena_procenta, 2),
                    "Měna": mena
                })
        except Exception:
            pass
        progres_bar.progress((i + 1) / len(seznam_tickeru), text=f"Načítám: {tkr}")
    
    progres_bar.empty()
    return pd.DataFrame(data_list)

df = nacti_data_portfolia(tickery)

# 4. Zobrazení aplikace
if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-box'><h3>Sledovaných pozic</h3><h2>40</h2></div>", unsafe_allow_html=True)
    with col2:
        Nejvice_rostouci = df.loc[df['Denní změna (%)'].idxmax()]
        st.markdown(f"<div class='metric-box'><h3>Dnešní skokan 🚀</h3><h2>{Nejvice_rostouci['Ticker']} ({Nejvice_rostouci['Denní změna (%)']}%)</h2></div>", unsafe_allow_html=True)
    with col3:
        trh_status = "Otevřen" if pd.Timestamp.now().hour in range(15, 22) else "Uzavřen (Zpožděná data)"
        st.markdown(f"<div class='metric-box'><h3>Stav trhu (USA)</h3><h2>{trh_status}</h2></div>", unsafe_allow_html=True)
        
    st.markdown("---")
    
    g1, g2 = st.columns([1, 1])
    
    with g1:
        st.subheader("📊 Denní pohyby cen (TOP 10)")
        top_10 = df.sort_values(by="Denní změna (%)", ascending=False).head(10)
        fig_bar = go.Figure(go.Bar(
            x=top_10['Ticker'],
            y=top_10['Denní změna (%)'],
            marker_color=['#2ecc71' if val >= 0 else '#e74c3c' for val in top_10['Denní změna (%)']]
        ))
        fig_bar.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

    with g2:
        st.subheader("🍕 Sektorové zastoupení")
        sektor_counts = df['Sektor'].value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=sektor_counts.index,
            values=sektor_counts.values,
            hole=.4
        ))
        fig_pie.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    st.subheader("📋 Kompletní přehled akciových titulů")
    vyhledavani = st.text_input("🔍 Rychlé vyhledávání akcie (napiš Ticker nebo název):")
    if vyhledavani:
        df_filtrovane = df[df['Ticker'].str.contains(vyhledavani, case=False) | df['Název společnosti'].str.contains(vyhledavani, case=False)]
    else:
        df_filtrovane = df
        
    st.dataframe(
        df_filtrovane.style.background_gradient(subset=['Denní změna (%)'], cmap='RdYlGn', vmin=-5, vmax=5),
        use_container_width=True,
        hide_index=True
    )
else:
    st.error("Nepodařilo se načíst data z Yahoo Finance. Zkontrolujte připojení nebo zkuste stránku obnovit.")
