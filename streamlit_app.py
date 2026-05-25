import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Moje Portfolio", layout="wide")

# --- VYNUCENÍ ČERNÉHO POZADÍ A STYLU ---
st.markdown("""
<style>
    /* Absolutně černé pozadí pro celou aplikaci */
    .stApp, .main {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    /* Úprava tabulek, aby ladily s černým pozadím */
    [data-testid="stDataFrame"] {
        background-color: #111111 !important;
    }
    /* Schování zbytečností */
    footer {visibility: hidden;}
    header {background: transparent !important;}
</style>
""", unsafe_allow_html=True)

# --- DEFINICE PORTFOLIA ---
TICKERS_1 = {
    "SXR8.DE": "SXR8.DE", "Gold": "GLD", "Meta": "META", "Tesla": "TSLA", 
    "Netflix": "NFLX", "Google": "GOOGL", "Spotify": "SPOT", "Microsoft": "MSFT", 
    "Amazon": "AMZN", "Nvidia": "NVDA", "Arm": "ARM", "AMD": "AMD", 
    "Lam Research": "LRCX", "Applied Materials": "AMAT", "Super Micro": "SMCI", 
    "Palantir": "PLTR", "Alibaba": "BABA", "McDonalds": "MCD", "Novo Nordisk": "NVO", 
    "LVMH": "MC.PA", "CVS": "CVS", "Nike": "NKE", "Starbucks": "SBUX", 
    "GameStop": "GME", "Bitcoin": "BTC-USD", "Coinbase": "COIN", "Robinhood": "HOOD"
}

TICKERS_2 = {
    "Pepsi": "PEP", "Coca Cola": "KO", "Realty Income": "O", "Pfizer": "PFE", 
    "JPMorgan": "JPM", "Uber": "UBER", "ČEZ": "CEZ.PR", "Broadcom": "AVGO", 
    "Micron": "MU", "SOFI": "SOFI", "Intel": "INTC", "QCOM": "QCOM", 
    "APP": "APP", "Serve Robotics": "SERV", "SPGI": "SPGI", "Dell": "DELL", 
    "UNH": "UNH"
}

# --- FUNKCE PRO NAČÍTÁNÍ DAT ---
@st.cache_data(ttl=60) # Data držíme v paměti 60 vteřin pro plynulost, pak se stahují nová
def get_portfolio_data(tickers_dict):
    data = []
    for name, ticker in tickers_dict.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d") # Bereme 5 dní pro jistotu přes víkendy
            
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
                "Akcie": name,
                "Ticker": ticker,
                "Cena ($)": current,
                "Předchozí ($)": prev_close,
                "Změna (%)": change_pct,
                "Změna ($)": change_val
            })
        except Exception:
            continue
    return pd.DataFrame(data)

# --- NAČTENÍ VŠECH DAT ---
with st.spinner('Synchronizuji data z trhů...'):
    df1 = get_portfolio_data(TICKERS_1)
    df2 = get_portfolio_data(TICKERS_2)

# --- TITULEK A DENNÍ NÁRŮST PORTFOLIA ---
st.title("📈 Moje Investiční Portfolio")

# Výpočet portfolia (1 ks od každé akcie)
if not df1.empty or not df2.empty:
    df_all = pd.concat([df1, df2], ignore_index=True)
    total_current_value = df_all["Cena ($)"].sum()
    total_prev_value = df_all["Předchozí ($)"].sum()
    
    portfolio_change_val = total_current_value - total_prev_value
    portfolio_change_pct = (portfolio_change_val / total_prev_value) * 100 if total_prev_value > 0 else 0
    
    st.metric(
        label="Denní nárůst portfolia (při držení 1 ks od každé pozice)",
        value=f"{total_current_value:,.2f} USD",
        delta=f"{portfolio_change_val:,.2f} USD ({portfolio_change_pct:+.2f} %)"
    )

st.markdown("---")
st.markdown("### Kliknutím na řádek v tabulce se zobrazí detailní graf")

# --- TABULKY S MOŽNOSTÍ KLIKNUTÍ ---
col_tab1, col_tab2 = st.columns(2)

def style_df(df):
    # Formátování tabulky pro hezký vzhled, nezobrazujeme technické sloupce
    display_df = df[["Akcie", "Cena ($)", "Změna (%)"]].copy()
    return display_df.style.map(
        lambda x: 'color: #00ff00; font-weight: bold' if x > 0 else ('color: #ff0000; font-weight: bold' if x < 0 else ''),
        subset=['Změna (%)']
    ).format({"Cena ($)": "{:.2f}", "Změna (%)": "{:+.2f} %"})

selected_ticker = None
selected_name = None

with col_tab1:
    st.write("**Tabulka 1: Růstové a Big Tech**")
    if not df1.empty:
        # Nová funkce Streamlitu: on_select vrací kliknutý řádek
        event1 = st.dataframe(
            style_df(df1), 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        if len(event1.selection.rows) > 0:
            row_idx = event1.selection.rows[0]
            selected_ticker = df1.iloc[row_idx]["Ticker"]
            selected_name = df1.iloc[row_idx]["Akcie"]

with col_tab2:
    st.write("**Tabulka 2: Hodnotové a Ostatní**")
    if not df2.empty:
        event2 = st.dataframe(
            style_df(df2), 
            use_container_width=True, 
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        if len(event2.selection.rows) > 0:
            row_idx = event2.selection.rows[0]
            selected_ticker = df2.iloc[row_idx]["Ticker"]
            selected_name = df2.iloc[row_idx]["Akcie"]

st.markdown("---")

# --- VYKRESLENÍ GRAFU PO KLIKNUTÍ ---
if selected_ticker:
    st.subheader(f"📊 Detail: {selected_name}")
    
    # Výběr času hned nad grafem
    timeframes = {
        "1 Den": ("1d", "1m"), 
        "1 Týden": ("5d", "15m"), 
        "1 Měsíc": ("1mo", "1d"), 
        "3 Měsíce": ("3mo", "1d"), 
        "Půl roku": ("6mo", "1d"), 
        "Od začátku roku (YTD)": ("ytd", "1d"), 
        "1 Rok": ("1y", "1d"), 
        "2 Roky": ("2y", "1wk"), 
        "5 Let": ("5y", "1wk"), 
        "Celá historie": ("max", "1mo")
    }
    
    # Horizontální radio buttons pro rychlé přepínání
    selected_tf_label = st.radio("Vyber časový úsek:", list(timeframes.keys()), horizontal=True)
    period, interval = timeframes[selected_tf_label]
    
    with st.spinner(f'Načítám graf pro {selected_name}...'):
        history_data = yf.download(selected_ticker, period=period, interval=interval, progress=False)
        
        if not history_data.empty:
            # Oprava pro pandas multiindex
            if isinstance(history_data.columns, pd.MultiIndex):
                history_data.columns = history_data.columns.droplevel(1)
            
            # Logika zelená/červená
            first_price = history_data['Close'].iloc[0]
            last_price = history_data['Close'].iloc[-1]
            line_color = '#00ff00' if last_price >= first_price else '#ff0000'
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history_data.index, 
                y=history_data['Close'],
                mode='lines',
                name=selected_name,
                line=dict(color=line_color, width=3),
                fill='tozeroy', # Lehké podbarvení pod křivkou pro lepší vizuál
                fillcolor=f"rgba({0 if line_color=='#00ff00' else 255}, {255 if line_color=='#00ff00' else 0}, 0, 0.1)"
            ))
            
            fig.update_layout(
                title=f"Vývoj ceny {selected_name} ({selected_ticker}) - Aktuální cena: {last_price:.2f}",
                xaxis_title="Čas",
                yaxis_title="Cena",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)', # Průhledné pozadí grafu, aby splynulo s černou
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Nepodařilo se stáhnout historická data pro tento časový úsek.")
else:
    st.info("👆 Klikni na jakoukoliv akcii v tabulkách výše pro zobrazení jejího detailního grafu.")
