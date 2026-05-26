import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# --- NASTAVENÍ STRÁNKY A AUTO-REFRESH ---
st.set_page_config(page_title="Moje Portfolio", layout="wide", initial_sidebar_state="expanded")

# --- VYNUCENÍ ČERNÉHO POZADÍ A CSS ---
st.markdown("""
<style>
    .stApp, .main, [data-testid="stSidebar"] {background-color: #000000 !important; color: #ffffff !important;}
    .stMarkdown p, .stText, label {color: #ffffff !important; font-weight: 600 !important;}
    [data-testid="stDataFrame"] {background-color: #111111 !important;}
    footer {visibility: hidden;} header {background: transparent !important;}
    a {color: #66b3ff !important; text-decoration: none; font-weight: 700 !important;}
    a:hover {text-decoration: underline; color: #99ccff !important;}
    
    /* Třídy pro obří čísla v hlavičce */
    .big-value {font-size: 3.5rem; font-weight: 900; margin-bottom: -10px; line-height: 1.1;}
    .big-profit {font-size: 2.2rem; font-weight: 800; color: #00ff00;}
    .big-loss {font-size: 2.2rem; font-weight: 800; color: #ff0000;}
    .big-neutral {font-size: 2.2rem; font-weight: 800; color: #ffffff;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACE NOVÉ PAMĚTI (MÉ PORTFOLIO A VYHLÍŽENÉ) ---
if 'MY_PORTFOLIO' not in st.session_state:
    st.session_state.MY_PORTFOLIO = {
        "SXR8.DE": {"tick": "SXR8.DE", "ks": 14.0}, "Gold": {"tick": "GLD", "ks": 16.0},
        "Meta": {"tick": "META", "ks": 2.0}, "Tesla": {"tick": "TSLA", "ks": 2.0},
        "Netflix": {"tick": "NFLX", "ks": 6.0}, "Google": {"tick": "GOOGL", "ks": 4.0},
        "Spotify": {"tick": "SPOT", "ks": 1.0}, "Microsoft": {"tick": "MSFT", "ks": 2.0},
        "Nvidia": {"tick": "NVDA", "ks": 5.0}, "Arm": {"tick": "ARM", "ks": 4.0},
        "AMD": {"tick": "AMD", "ks": 4.0}, "Lam Research": {"tick": "LRCX", "ks": 5.0},
        "Applied Mat.": {"tick": "AMAT", "ks": 2.0}, "Super Micro": {"tick": "SMCI", "ks": 14.0},
        "Palantir": {"tick": "PLTR", "ks": 6.0}, "Alibaba": {"tick": "BABA", "ks": 4.0},
        "McDonalds": {"tick": "MCD", "ks": 1.0}, "Novo Nordisk": {"tick": "NVO", "ks": 8.0},
        "LVMH": {"tick": "MC.PA", "ks": 1.0}, "CVS": {"tick": "CVS", "ks": 5.0},
        "Nike": {"tick": "NKE", "ks": 3.0}, "Starbucks": {"tick": "SBUX", "ks": 2.0},
        "GameStop": {"tick": "GME", "ks": 4.0}, "Bitcoin": {"tick": "BTC-USD", "ks": 0.153},
        "Coinbase": {"tick": "COIN", "ks": 10.0}, "Robinhood": {"tick": "HOOD", "ks": 20.0}
    }

if 'MY_WATCHLIST' not in st.session_state:
    st.session_state.MY_WATCHLIST = {
        "Pepsi": "PEP", "Coca Cola": "KO", "Realty Income": "O", "Pfizer": "PFE", 
        "JPMorgan": "JPM", "Uber": "UBER", "ČEZ": "CEZ.PR", "Broadcom": "AVGO", 
        "Micron": "MU", "SOFI": "SOFI", "Intel": "INTC", "QCOM": "QCOM", 
        "APP": "APP", "Serve Rob.": "SERV", "SPGI": "SPGI", "Dell": "DELL", "UNH": "UNH"
    }

# --- POSTRANNÍ PANEL (OVLÁDÁNÍ A REFRESH) ---
st.sidebar.header("⚙️ Nástroje a správa")
auto_ref = st.sidebar.checkbox("🔄 Auto-aktualizace (každých 60s)", value=False)
if auto_ref:
    st.markdown('<meta http-equiv="refresh" content="60">', unsafe_allow_html=True)

if st.sidebar.button("⚡ Aktualizovat ceny HNED", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Přidat akcii do vyhlížených")
new_n = st.sidebar.text_input("Název (např. Apple)")
new_t = st.sidebar.text_input("Ticker (např. AAPL)")
if st.sidebar.button("➕ Přidat vyhlíženou"):
    if new_n and new_t:
        st.session_state.MY_WATCHLIST[new_n] = new_t.upper()
        st.cache_data.clear()
        st.rerun()

# --- NAČÍTÁNÍ DAT ---
@st.cache_data(ttl=50)
def get_data_owned(port_dict):
    d = []
    for n, info in port_dict.items():
        try:
            tk = info['tick']
            ks = info['ks']
            stk = yf.Ticker(tk)
            hst = stk.history(period="5d").dropna(subset=['Close'])
            hst = hst[hst['Close'] > 0]
            if len(hst) >= 2:
                p_cl = hst['Close'].iloc[-2]
                c_cl = hst['Close'].iloc[-1]
                ch_v = c_cl - p_cl
                ch_p = (ch_v / p_cl) * 100
            elif len(hst) == 1:
                p_cl = c_cl = hst['Close'].iloc[0]
                ch_v = ch_p = 0.0
            else: continue
            
            val_now = c_cl * ks
            val_prev = p_cl * ks
            day_profit = val_now - val_prev
            
            d.append({
                "Akcie": n, "Ticker": tk, "Cena ($)": c_cl, "Změna (%)": ch_p, 
                "Ks": ks, "Hodnota ($)": val_now, "Denní Zisk ($)": day_profit
            })
        except: continue
    return pd.DataFrame(d)

@st.cache_data(ttl=50)
def get_data_watch(watch_dict):
    d = []
    for n, tk in watch_dict.items():
        try:
            stk = yf.Ticker(tk)
            hst = stk.history(period="5d").dropna(subset=['Close'])
            if len(hst) >= 2:
                p_cl = hst['Close'].iloc[-2]
                c_cl = hst['Close'].iloc[-1]
                ch_p = ((c_cl - p_cl) / p_cl) * 100
            else: continue
            d.append({"Akcie": n, "Ticker": tk, "Cena ($)": c_cl, "Změna (%)": ch_p})
        except: continue
    return pd.DataFrame(d)

with st.spinner('Stahuji aktuální ceny a propočítávám portfolio...'):
    df_own = get_data_owned(st.session_state.MY_PORTFOLIO)
    df_wat = get_data_watch(st.session_state.MY_WATCHLIST)

# --- HLAVNÍ OBŘÍ METRIKA PORTFOLIA ---
st.markdown("<h1 style='text-align: center; color: #ffffff;'>📈 Můj Investiční Přehled</h1>", unsafe_allow_html=True)

if not df_own.empty:
    tot_val = df_own["Hodnota ($)"].sum()
    tot_prof = df_own["Denní Zisk ($)"].sum()
    tot_prev = tot_val - tot_prof
    tot_pct = (tot_prof / tot_prev) * 100 if tot_prev > 0 else 0
    
    css_class = "big-profit" if tot_prof > 0 else ("big-loss" if tot_prof < 0 else "big-neutral")
    sign = "+" if tot_prof > 0 else ""
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="color: #aaaaaa; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px;">Aktuální Hodnota Portfolia</div>
        <div class="big-value">${tot_val:,.2f}</div>
        <div class="{css_class}">{sign}{tot_prof:,.2f} $ ({sign}{tot_pct:,.2f} %) Dnes</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("### 📊 Přehled akcií")

col_t1, col_t2 = st.columns(2)

def style_own(df):
    d = df[["Akcie", "Cena ($)", "Změna (%)", "Ks", "Hodnota ($)"]].copy()
    return d.style.map(
        lambda x: 'color: #00ff00; font-weight: 900' if x > 0 else ('color: #ff0000; font-weight: 900' if x < 0 else 'color: #ffffff; font-weight: 900'),
        subset=['Změna (%)']
    ).format({"Cena ($)": "{:.2f}", "Změna (%)": "{:+.2f} %", "Ks": "{:.3f}", "Hodnota ($)": "{:,.2f}"})

def style_wat(df):
    d = df[["Akcie", "Cena ($)", "Změna (%)"]].copy()
    return d.style.map(
        lambda x: 'color: #00ff00; font-weight: 900' if x > 0 else ('color: #ff0000; font-weight: 900' if x < 0 else 'color: #ffffff; font-weight: 900'),
        subset=['Změna (%)']
    ).format({"Cena ($)": "{:.2f}", "Změna (%)": "{:+.2f} %"})

sel_t, sel_n = None, None

with col_t1:
    st.write("**Mé portfolio (držené akcie)**")
    if not df_own.empty:
        df_own = df_own.sort_values(by="Hodnota ($)", ascending=False)
        e1 = st.dataframe(style_own(df_own), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        if len(e1.selection.rows) > 0:
            sel_t = df_own.iloc[e1.selection.rows[0]]["Ticker"]
            sel_n = df_own.iloc[e1.selection.rows[0]]["Akcie"]

with col_t2:
    st.write("**Vyhlížené akcie (watchlist)**")
    if not df_wat.empty:
        e2 = st.dataframe(style_wat(df_wat), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row")
        if len(e2.selection.rows) > 0:
            sel_t = df_wat.iloc[e2.selection.rows[0]]["Ticker"]
            sel_n = df_wat.iloc[e2.selection.rows[0]]["Akcie"]

st.markdown("---")

# --- DETAIL, GRAF A ZPRÁVY ---
if sel_t:
    st.subheader(f"📈 Analýza: {sel_n} ({sel_t})")
    
    tf = {
        "1 Den": ("1d", "1m"), "1 Týden": ("5d", "15m"), "1 Měsíc": ("1mo", "1d"), 
        "3 Měsíce": ("3mo", "1d"), "Půl roku": ("6mo", "1d"), "YTD": ("ytd", "1d"), 
        "1 Rok": ("1y", "1d"), "2 Roky": ("2y", "1wk"), "Celá historie": ("max", "1mo")
    }
    sel_tf = st.radio("Vyber časový horizont grafu:", list(tf.keys()), horizontal=True)
    per, inter = tf[sel_tf]

    with st.spinner(f'Stahuji detaily pro {sel_n}...'):
        stk = yf.Ticker(sel_t)
        
        # Opravené robustní stažení P/E a 52week limitů (obejití restrikcí)
        pe_val, hi_52, lo_52 = "N/A", "N/A", "N/A"
        try:
            fi = stk.fast_info
            if hasattr(fi, 'year_high'): hi_52 = round(fi.year_high, 2)
            if hasattr(fi, 'year_low'): lo_52 = round(fi.year_low, 2)
            
            inf = stk.info
            p_r = inf.get('trailingPE', 'N/A')
            if isinstance(p_r, (int, float)): pe_val = round(p_r, 2)
        except: pass

        try:
            h_df = yf.download(sel_t, period=per, interval=inter, progress=False)
            if not h_df.empty:
                if isinstance(h_df.columns, pd.MultiIndex): h_df.columns = h_df.columns.droplevel(1)
                h_df = h_df.dropna(subset=['Close'])
                h_df = h_df[h_df['Close'] > 0]
                
                fp, lp = h_df['Close'].iloc[0], h_df['Close'].iloc[-1]
                pch = ((lp - fp) / fp) * 100
                clr = '#00ff00' if lp >= fp else '#ff0000'
                
                m1, m2, m3 = st.columns(3)
                m1.metric(f"Vývoj ceny za ({sel_tf})", f"{lp:.2f}", delta=f"{pch:+.2f} %")
                m2.metric("P/E Ratio", pe_val)
                m3.metric("Min / Max (52 týdnů)", f"{lo_52} / {hi_52}")
                st.write("")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=h_df.index, y=h_df['Close'], mode='lines', name=sel_n, line=dict(color=clr, width=3), fill='tozeroy', fillcolor=f"rgba({0 if clr=='#00ff00' else 255}, {255 if clr=='#00ff00' else 0}, 0, 0.1)"))
                fig.add_hline(y=lp, line_dash="dot", line_color="white", annotation_text=f"CENA: {lp:.2f}", annotation_position="top left", annotation_font=dict(size=16, color="white", family="Arial Black"))
                fig.update_layout(xaxis_title="Čas", yaxis_title="Cena", template="plotly_dark", yaxis=dict(range=[h_df['Close'].min()*0.99, h_df['Close'].max()*1.01]), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Nelze vykreslit graf.")

    # --- SEZÓNNOST (Přesunuta pod graf) ---
    with st.expander("📅 Zobrazit Sezónnost (Měsíční výnosy v %)"):
        with st.spinner('Počítám sezónnost...'):
            try:
                s_df = yf.download(sel_t, period="10y", interval="1mo", progress=False)
                if not s_df.empty:
                    if isinstance(s_df.columns, pd.MultiIndex): s_df.columns = s_df.columns.droplevel(1)
                    s_df = s_df.dropna(subset=['Close'])
                    s_df['Ret'] = s_df['Close'].pct_change() * 100
                    s_df = s_df.dropna(subset=['Ret'])
                    s_df['Rok'] = s_df.index.year
                    s_df['Měsíc'] = s_df.index.month
                    p_df = s_df.pivot(index='Rok', columns='Měsíc', values='Ret').sort_index(ascending=False)
                    mn = {1:'Leden', 2:'Únor', 3:'Březen', 4:'Duben', 5:'Květen', 6:'Červen', 7:'Červenec', 8:'Srpen', 9:'Září', 10:'Říjen', 11:'Listopad', 12:'Prosinec'}
                    p_df = p_df.rename(columns=mn)
                    def s_cs(v): return '' if pd.isna(v) else f"color: {'#00ff00' if v>0 else '#ff0000'}; font-weight: bold; font-size: 1.1rem;"
                    st.dataframe(p_df.style.map(s_cs).format("{:+.2f} %", na_rep="-"), use_container_width=True)
            except: st.error("Data sezónnosti nejsou dostupná.")

    # --- ZPRÁVY SEŘAZENÉ PODLE DATA ---
    st.markdown("### 📰 Aktuální zprávy (v češtině)")
    try:
        q = f'"{sel_n}" akcie OR "{sel_t}"'
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=cs&gl=CZ&ceid=CZ:cs"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=5).read())
        
        n_lst = []
        for it in root.findall('./channel/item')[:20]:
            t = it.find('title').text
            l = it.find('link').text
            s = it.find('source').text if it.find('source') is not None else "Google News"
            pd = it.find('pubDate').text
            try:
                dt_obj = datetime.strptime(pd[:-4], "%a, %d %b %Y %H:%M:%S")
                d_str = dt_obj.strftime("%d.%m.%Y %H:%M")
            except:
                dt_obj = datetime.min
                d_str = pd
            n_lst.append({"t": t, "l": l, "s": s, "d_str": d_str, "dt_obj": dt_obj})
        
        # Striktní seřazení od nejnovějších
        n_lst.sort(key=lambda x: x["dt_obj"], reverse=True)
        
        if len(n_lst) > 0:
            for it in n_lst[:7]:
                st.markdown(f"**[{it['t']}]({it['l']})**")
                st.caption(f"🗞️ {it['s']} | 🕒 {it['d_str']}")
                st.write("")
        else:
            st.info("Žádné zprávy v češtině.")
    except: st.warning("Nepodařilo se načíst zprávy.")
else:
    st.info("👆 Klikni na akcii v tabulkách výše pro zobrazení detailní analýzy.")
