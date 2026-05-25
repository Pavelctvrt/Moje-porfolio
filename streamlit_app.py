import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(
    page_title="Moje Portfolio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VYNUCENÍ ČERNÉHO POZADÍ A MAXIMÁLNÍ ČITELNOSTI ---
st.markdown("""
<style>
    .stApp, .main, [data-testid="stSidebar"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .stMarkdown p, .stText, label, .stMetricLabel, [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stDataFrame"] {
        background-color: #111111 !important;
    }
    footer {visibility: hidden;}
    header {background: transparent !important;}
    
    /* PÍSMO PRO ČLÁNKY - Zářivě světle modrá a tučná */
    a {color: #66b3ff !important; text-decoration: none; font-weight: 700 !important;}
    a:hover {text-decoration: underline; color: #99ccff !important;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACE PORTFOLIA V SESSION STATE ---
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
        "APP": "APP", "Serve Robotics": "SERV", "SPGI": "SPGI", "Dell": "DELL", 
        "UNH": "UNH"
    }

# --- POSTRANNÍ PANEL ---
st.sidebar.header("⚙️ Správa akcií")
st.sidebar.subheader("Přidat novou")
new_name = st.sidebar.text_input("Název (např. Apple)")
new_ticker = st.sidebar.text_input("Ticker (např. AAPL)")
target_table = st.sidebar.radio("Kam přidat?", ["Tabulka 1", "Tabulka 2"])

if st.sidebar.button("➕ Přidat akcii"):
    if new_name and new_ticker:
        if "1" in target_table:
            st.session_state.TICKERS_1[new_name] = new_ticker.upper()
        else:
            st.session_state.TICKERS_2[new_name] = new_ticker.upper()
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Odebrat existující")
all_current_stocks = {**st.session_state.TICKERS_1, **st.session_state.TICKERS_2}
stock_to_remove = st.sidebar.selectbox("Vyber akcii k odebrání", [""] + list(all_current_stocks.keys()))

if st.sidebar.button("❌ Odebrat akcii"):
    if stock_to_remove:
        if stock_to_remove in st.session_state.TICKERS_1:
            del st.session_state.TICKERS_1[stock_to_remove]
        elif stock_to_remove in st.session_state.TICKERS_2:
            del st.session_state.TICKERS_2[stock_to_remove]
        st.cache_data.clear()
        st.rerun()

# --- FUNKCE PRO NAČÍTÁNÍ DATA ---
@st.cache_data(ttl=60)
def get_portfolio_data(tickers_dict):
    data = []
    for name, ticker in tickers_dict.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            hist = hist.dropna(subset=['Close'])
            hist = hist[hist['Close'] > 0]
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
                "Akcie": name, "Ticker": ticker, "Cena ($)": current,
                "Předchozí ($)": prev_close, "Změna (%)": change_pct, "Změna ($)": change_val
            })
        except Exception:
            continue
    return pd.DataFrame(data)

with st.spinner('Synchronizuji data z trhů...'):
    df1 = get_portfolio_data(st.session_state.TICKERS_1)
    df2 = get_portfolio_data(st.session_state.TICKERS_2)

# --- HLAVNÍ METRIKA ---
st.title("📈 Moje Investiční Portfolio")

if not df1.empty or not df2.empty:
    df_all = pd.concat([df1, df2], ignore_index=True)
    v_cur = df_all["Cena ($)"].sum()
    v_prev = df_all["Předchozí ($)"].sum()
    ch_val = v_cur - v_prev
    ch_pct = (ch_val / v_prev) * 100 if v_prev > 0 else 0
    
    st.metric(
        label="Denní nárůst portfolia (při držení 1 ks od každé pozice)",
        value=f"{v_cur:,.2f} USD",
        delta=f"{ch_val:,.2f} USD ({ch_pct:+.2f} %)"
    )

st.markdown("---")
st.markdown("### Přehled akcií")
sort_option = st.radio("Rychlé řazení:", ["Výchozí", "🚀 Růst", "📉 Pokles"], horizontal=True)

if sort_option == "🚀 Růst":
    if not df1.empty: df1 = df1.sort_values(by="Změna (%)", ascending=False)
    if not df2.empty: df2 = df2.sort_values(by="Změna (%)", ascending=False)
elif sort_option == "📉 Pokles":
    if not df1.empty: df1 = df1.sort_values(by="Změna (%)", ascending=True)
    if not df2.empty: df2 = df2.sort_values(by="Změna (%)", ascending=True)

col_tab1, col_tab2 = st.columns(2)

def style_df(df):
    display_df = df[["Akcie", "Cena ($)", "Změna (%)"]].copy()
    return display_df.style.map(
        lambda x: 'color: #00ff00; font-weight: 900' if x > 0 else ('color: #ff0000; font-weight: 900' if x < 0 else 'color: #ffffff; font-weight: 900'),
        subset=['Změna (%)']
    ).format({"Cena ($)": "{:.2f}", "Změna (%)": "{:+.2f} %"})

selected_ticker, selected_name = None, None

with col_tab1:
    st.write("**Tabulka 1: Růstové a Big Tech**")
    if not df1.empty:
        # Rozsekané řádky proti uřezávání na GitHubu
        ev1 = st.dataframe(
            style_df(df1),
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        if len(ev1.selection.rows) > 0:
            selected_ticker = df1.iloc[ev1.selection.rows[0]]["Ticker"]
            selected_name = df1.iloc[ev1.selection.rows[0]]["Akcie"]

with col_tab2:
    st.write("**Tabulka 2: Hodnotové a Ostatní**")
    if not df2.empty:
        # Rozsekané řádky proti uřezávání na GitHubu
        ev2 = st.dataframe(
            style_df(df2),
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        if len(ev2.selection.rows) > 0:
            selected_ticker = df2.iloc[ev2.selection.rows[0]]["Ticker"]
            selected_name = df2.iloc[ev2.selection.rows[0]]["Akcie"]

st.markdown("---")

# --- DETAIL, GRAF, SEZÓNNOST, ZPRÁVY ---
if selected_ticker:
    st.subheader(f"📊 Detail: {selected_name} ({selected_ticker})")
    with st.spinner(f'Načítám {selected_name}...'):
        stock = yf.Ticker(selected_ticker)
        pe_ratio, high_52, low_52 = 'N/A', 'N/A', 'N/A'
        try:
            inf = stock.info
            pe_raw = inf.get('trailingPE', 'N/A')
            if isinstance(pe_raw, (int, float)): pe_ratio = round(pe_raw, 2)
            high_52 = inf.get('fiftyTwoWeekHigh', 'N/A')
            low_52 = inf.get('fiftyTwoWeekLow', 'N/A')
        except: pass
        
        m1, m2, m3 = st.columns(3)
        ak_data = df_all.loc[df_all['Ticker'] == selected_ticker]
        c_tab = ak_data['Cena ($)'].values[0]
        p_tab = ak_data['Změna (%)'].values[0]
        
        m1.metric("Aktuální cena", f"{c_tab:.2f}", delta=f"{p_tab:+.2f} %")
        m2.metric("P/E Ratio", pe_ratio)
        m3.metric("Min / Max (52 týdnů)", f"{low_52} / {high_52}" if low_52 != 'N/A' else "N/A")
        st.markdown("<br>", unsafe_allow_html=True)
        
        tf = {
            "1D": ("1d", "1m"), "1T": ("5d", "15m"), "1M": ("1mo", "1d"), "3M": ("3mo", "1d"), 
            "6M": ("6mo", "1d"), "YTD": ("ytd", "1d"), "1R": ("1y", "1d"), "2R": ("2y", "1wk"), 
            "5L": ("5y", "1wk"), "MAX": ("max", "1mo")
        }
        sel_tf = st.radio("Časový úsek:", list(tf.keys()), horizontal=True)
        period, interval = tf[sel_tf]
        
        try:
            h_df = yf.download(selected_ticker, period=period, interval=interval, progress=False)
            if not h_df.empty:
                if isinstance(h_df.columns, pd.MultiIndex): h_df.columns = h_df.columns.droplevel(1)
                h_df = h_df.dropna(subset=['Close'])
                h_df = h_df[h_df['Close'] > 0]
                f_pr, l_pr = h_df['Close'].iloc[0], h_df['Close'].iloc[-1]
                col = '#00ff00' if l_pr >= f_pr else '#ff0000'
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=h_df.index, y=h_df['Close'], mode='lines', name=selected_name, line=dict(color=col, width=3), fill='tozeroy', fillcolor=f"rgba({0 if col=='#00ff00' else 255}, {255 if col=='#00ff00' else 0}, 0, 0.1)"))
                fig.add_hline(y=l_pr, line_dash="dot", line_color="white", annotation_text=f"AKT. CENA: {l_pr:.2f}", annotation_position="top left", annotation_font=dict(size=16, color="white", family="Arial Black"))
                fig.update_layout(xaxis_title="Čas", yaxis_title="Cena", template="plotly_dark", yaxis=dict(range=[h_df['Close'].min()*0.99, h_df['Close'].max()*1.01]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", font=dict(color="white", size=14))
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Chyba grafu.")

    # --- ČESKÉ GOOGLE ZPRÁVY S DATEM ---
    st.markdown("### 📰 Aktuální zprávy (v češtině)")
    try:
        q = f'"{selected_name}" akcie OR "{selected_ticker}"'
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=cs&gl=CZ&ceid=CZ:cs"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=5).read())
        found = False
        for item in root.findall('./channel/item')[:7]:
            found = True
            t_str = item.find('title').text
            l_str = item.find('link').text
            src = item.find('source').text if item.find('source') is not None else "Google News"
            
            p_date = item.find('pubDate').text
            try:
                dt_parsed = datetime.strptime(p_date[:-4], "%a, %d %b %Y %H:%M:%S")
                d_str = dt_parsed.strftime("%d.%m.%Y %H:%M")
            except:
                d_str = p_date
                
            st.markdown(f"**[{t_str}]({l_str})**")
            st.caption(f"🗞️ {src} | 🕒 {d_str}")
            st.write("")
        if not found: st.info("Žádné české články.")
    except: st.warning("Zprávy nedostupné.")

    # --- SEZÓNNOST ---
    with st.expander("📅 Zobrazit Sezónnost (Měsíční výnosy v %)"):
        with st.spinner('Počítám...'):
            try:
                s_df = yf.download(selected_ticker, period="10y", interval="1mo", progress=False)
                if not s_df.empty:
                    if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.droplevel(1)
                    s_df = s_df.dropna(subset=['Close'])
                    s_df = s_df[s_df['Close'] > 0]
                    s_df['Return'] = s_df['Close'].pct_change() * 100
                    s_df = s_df.dropna(subset=['Return'])
                    s_df['Rok'] = s_df.index.year
                    s_df['Měsíc'] = s_df.index.month
                    p_df = s_df.pivot(index='Rok', columns='Měsíc', values='Return').sort_index(ascending=False)
                    m_names = {1:'Leden', 2:'Únor', 3:'Březen', 4:'Duben', 5:'Květen', 6:'Červen', 7:'Červenec', 8:'Srpen', 9:'Září', 10:'Říjen', 11:'Listopad', 12:'Prosinec'}
                    p_df = p_df.rename(columns=m_names)
                    def st_s(v): return '' if pd.isna(v) else f"color: {'#00ff00' if v > 0 else '#ff0000'}; font-weight: bold; font-size: 1.1rem;"
                    st.dataframe(p_df.style.map(st_s).format("{:+.2f} %", na_rep="-"), use_container_width=True)
            except: st.error("Sezónnost nedostupná.")
else:
    st.info("👆 Klikni na jakoukoliv akcii v tabulkách výše pro zobrazení detailů.")
