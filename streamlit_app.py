import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Moje Portfolio", layout="wide", initial_sidebar_state="collapsed")

# --- VYNUCENÍ ČERNÉHO POZADÍ A CSS ---
st.markdown("""
<style>
    .stApp, .main, [data-testid="stSidebar"] {background-color: #000000 !important; color: #ffffff !important;}
    .stMarkdown p, .stText, label {color: #ffffff !important; font-weight: 600 !important;}
    [data-testid="stDataFrame"] {background-color: #111111 !important;}
    footer {visibility: hidden;} header {background: transparent !important;}
    a {color: #66b3ff !important; text-decoration: none; font-weight: 700 !important;}
    a:hover {text-decoration: underline; color: #99ccff !important;}
    
    [data-testid="stSidebar"] {left: auto !important; right: 0 !important; border-left: 1px solid #333 !important; border-right: none !important;}
    [data-testid="collapsedControl"] {left: auto !important; right: 1rem !important;}
    
    .big-value {font-size: 3.5rem; font-weight: 900; margin-bottom: -10px; line-height: 1.1;}
    .big-profit {font-size: 2.2rem; font-weight: 800; color: #00ff00;}
    .big-loss {font-size: 2.2rem; font-weight: 800; color: #ff0000;}
    .big-neutral {font-size: 2.2rem; font-weight: 800; color: #ffffff;}
    .detail-price {font-size: 2.2rem; font-weight: 900; line-height: 1.1;}
    .detail-pct-up {font-size: 2rem; font-weight: 900; color: #00ff00;}
    .detail-pct-down {font-size: 2rem; font-weight: 900; color: #ff0000;}
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACE PAMĚTI ---
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

if 'sel_ticker' not in st.session_state:
    st.session_state.sel_ticker = None
    st.session_state.sel_name = None

# --- POSTRANNÍ PANEL ---
st.sidebar.header("⚙️ Nástroje a správa")
st.sidebar.checkbox("🔄 Živá aktualizace (30s)", value=False, key="auto_refresh")

if st.sidebar.button("⚡ Aktualizovat HNED", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Přidat akcii")
new_n = st.sidebar.text_input("Název (např. Apple)")
new_t = st.sidebar.text_input("Ticker (např. AAPL)")
target_table = st.sidebar.radio("Kam přidat?", ["Mé portfolio", "Vyhlížené"])

if st.sidebar.button("➕ Přidat"):
    if new_n and new_t:
        if "Mé" in target_table:
            st.session_state.MY_PORTFOLIO[new_n] = {"tick": new_t.upper(), "ks": 0.0}
        else:
            st.session_state.MY_WATCHLIST[new_n] = new_t.upper()
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Odebrat akcii")
all_stocks = list(st.session_state.MY_PORTFOLIO.keys()) + list(st.session_state.MY_WATCHLIST.keys())
stock_to_remove = st.sidebar.selectbox("Vyber k odebrání", [""] + all_stocks)
if st.sidebar.button("❌ Odebrat"):
    if stock_to_remove:
        if stock_to_remove in st.session_state.MY_PORTFOLIO: del st.session_state.MY_PORTFOLIO[stock_to_remove]
        if stock_to_remove in st.session_state.MY_WATCHLIST: del st.session_state.MY_WATCHLIST[stock_to_remove]
        st.cache_data.clear()
        st.rerun()

# --- NAČÍTÁNÍ DAT ---
@st.cache_data(ttl=15)
def get_data_owned(port_dict):
    d = []
    for n, info in port_dict.items():
        try:
            tk = info['tick']
            ks = info['ks']
            stk = yf.Ticker(tk)
            hst = stk.history(period="5d").dropna(subset=['Close'])
            if len(hst) >= 2:
                p_cl = hst['Close'].iloc[-2]
                c_cl = hst['Close'].iloc[-1]
            elif len(hst) == 1:
                p_cl = c_cl = hst['Close'].iloc[0]
            else: continue
            
            ch_p = ((c_cl - p_cl) / p_cl) * 100 if p_cl > 0 else 0
            val_now = c_cl * ks
            val_prev = p_cl * ks
            day_profit = val_now - val_prev
            
            d.append({"Akcie": n, "Ticker": tk, "Cena ($)": c_cl, "Změna (%)": ch_p, "Hodnota ($)": val_now, "Denní Zisk ($)": day_profit})
        except: continue
    return pd.DataFrame(d)

@st.cache_data(ttl=15)
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

@st.cache_data(ttl=300)
def get_portfolio_history(port_dict):
    tickers = [info['tick'] for info in port_dict.values() if info['ks'] > 0]
    if not tickers: return None
    try:
        data = yf.download(tickers, period="1y", interval="1d", progress=False)
        if data.empty: return None
        
        if isinstance(data.columns, pd.MultiIndex):
            closes = data['Close'].ffill().bfill()
        else:
            closes = pd.DataFrame({tickers[0]: data['Close']}).ffill().bfill()
            
        port_series = pd.Series(0.0, index=closes.index)
        for _, info in port_dict.items():
            t = info['tick']
            k = info['ks']
            if k > 0 and t in closes.columns:
                port_series += closes[t] * k
        return port_series
    except:
        return None

with st.spinner('Stahuji aktuální ceny z burzy...'):
    df_own = get_data_owned(st.session_state.MY_PORTFOLIO)
    df_wat = get_data_watch(st.session_state.MY_WATCHLIST)
    port_hist = get_portfolio_history(st.session_state.MY_PORTFOLIO)

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
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="color: #aaaaaa; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px;">Aktuální Hodnota Portfolia</div>
        <div class="big-value">${tot_val:,.2f}</div>
        <div class="{css_class}">{sign}{tot_prof:,.2f} $ ({sign}{tot_pct:,.2f} %) Dnes</div>
    </div>
    """, unsafe_allow_html=True)

    # --- HISTORICKÝ VÝVOJ PORTFOLIA ---
    if port_hist is not None and len(port_hist) > 5:
        cur_val = port_hist.iloc[-1]
        
        def calc_hist(days_back):
            if len(port_hist) > days_back:
                old_v = port_hist.iloc[-days_back]
                diff = cur_val - old_v
                pct = (diff / old_v) * 100 if old_v > 0 else 0
                return diff, pct
            return None, None

        w1_d, w1_p = calc_hist(6)
        m1_d, m1_p = calc_hist(22)
        m6_d, m6_p = calc_hist(126)
        y1_d, y1_p = calc_hist(min(252, len(port_hist)-1))

        st.markdown("<div style='text-align: center; color: #aaaaaa; margin-bottom: 10px; font-size: 0.9rem;'>Historický vývoj (při současném složení)</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        if w1_p is not None: c1.metric("1 Týden", f"{w1_p:+.2f} %", f"{w1_d:+.0f} $")
        if m1_p is not None: c2.metric("1 Měsíc", f"{m1_p:+.2f} %", f"{m1_d:+.0f} $")
        if m6_p is not None: c3.metric("Půl roku", f"{m6_p:+.2f} %", f"{m6_d:+.0f} $")
        if y1_p is not None: c4.metric("1 Rok", f"{y1_p:+.2f} %", f"{y1_d:+.0f} $")
        
        st.write("")

st.markdown("---")
st.markdown("### 📊 Přehled akcií")

col_t1, col_t2 = st.columns(2)

def style_table(df):
    d = df[["Akcie", "Cena ($)", "Změna (%)"]].copy()
    return d.style.map(
        lambda x: 'color: #00ff00; font-weight: 900' if x > 0 else ('color: #ff0000; font-weight: 900' if x < 0 else 'color: #ffffff; font-weight: 900'),
        subset=['Změna (%)']
    ).format({"Cena ($)": "{:.2f}", "Změna (%)": "{:+.2f} %"})

temp_ticker, temp_name = None, None

with col_t1:
    st.write("**Mé portfolio**")
    if not df_own.empty:
        df_own = df_own.sort_values(by="Hodnota ($)", ascending=False).reset_index(drop=True)
        e1 = st.dataframe(style_table(df_own), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row", key="t1")
        if len(e1.selection.rows) > 0:
            temp_ticker = df_own.iloc[e1.selection.rows[0]]["Ticker"]
            temp_name = df_own.iloc[e1.selection.rows[0]]["Akcie"]

with col_t2:
    st.write("**Vyhlížené akcie**")
    if not df_wat.empty:
        df_wat = df_wat.reset_index(drop=True)
        e2 = st.dataframe(style_table(df_wat), use_container_width=True, hide_index=True, on_select="rerun", selection_mode="single-row", key="t2")
        if len(e2.selection.rows) > 0:
            temp_ticker = df_wat.iloc[e2.selection.rows[0]]["Ticker"]
            temp_name = df_wat.iloc[e2.selection.rows[0]]["Akcie"]

if temp_ticker is not None:
    st.session_state.sel_ticker = temp_ticker
    st.session_state.sel_name = temp_name

st.markdown("---")

# --- DETAIL A ZPRÁVY BEZ GRAFU ---
if st.session_state.sel_ticker:
    sel_t = st.session_state.sel_ticker
    sel_n = st.session_state.sel_name
    st.subheader(f"📈 Analýza: {sel_n} ({sel_t})")
    
    tf = {
        "1 Den": ("1d", "1m"), "1 Týden": ("5d", "15m"), "1 Měsíc": ("1mo", "1d"), 
        "3 Měsíce": ("3mo", "1d"), "Půl roku": ("6mo", "1d"), "YTD": ("ytd", "1d"), 
        "1 Rok": ("1y", "1d"), "2 Roky": ("2y", "1wk"), "Celá historie": ("max", "1mo")
    }
    sel_tf = st.radio("Vyber časový horizont pro výpočet změny:", list(tf.keys()), horizontal=True)
    per, inter = tf[sel_tf]

    with st.spinner(f'Stahuji detaily pro {sel_n}...'):
        stk = yf.Ticker(sel_t)
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
                clr_class = 'detail-pct-up' if lp >= fp else 'detail-pct-down'
                sign = '+' if lp >= fp else ''
                
                m1, m2, m3 = st.columns([2, 1, 1])
                with m1:
                    st.markdown(f"""
                    <div>
                        <div style="color: #aaaaaa; font-size: 1rem; text-transform: uppercase;">Vývoj ceny ({sel_tf})</div>
                        <div class="detail-price">${lp:.2f}</div>
                        <div class="{clr_class}">{sign}{pch:.2f} %</div>
                    </div>
                    """, unsafe_allow_html=True)
                m2.metric("P/E Ratio", pe_val)
                m3.metric("Min / Max (52 týdnů)", f"{lo_52} / {hi_52}")
                st.write("")
                
        except: st.error("Nelze stáhnout data pro tento časový úsek.")

    # --- SEZÓNNOST ---
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

    # --- ZPRÁVY ---
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
            pd_str = it.find('pubDate').text
            try:
                dt_obj = datetime.strptime(pd_str[:-4], "%a, %d %b %Y %H:%M:%S")
                d_str = dt_obj.strftime("%d.%m.%Y %H:%M")
            except:
                dt_obj = datetime.min
                d_str = pd_str
            n_lst.append({"t": t, "l": l, "s": s, "d_str": d_str, "dt_obj": dt_obj})
        n_lst.sort(key=lambda x: x["dt_obj"], reverse=True)
        if len(n_lst) > 0:
            for it in n_lst[:7]:
                st.markdown(f"**[{it['t']}]({it['l']})**")
                st.caption(f"🗞️ {it['s']} | 🕒 {it['d_str']}")
                st.write("")
        else: st.info("Žádné zprávy v češtině.")
    except: st.warning("Nepodařilo se načíst zprávy.")
else:
    st.info("👆 Klikni na akcii v tabulkách výše pro zobrazení detailní analýzy.")

if st.session_state.auto_refresh:
    time.sleep(30)
    st.rerun()
