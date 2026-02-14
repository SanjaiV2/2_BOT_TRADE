import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import os
from ai_brain import get_ai_prediction

# --- CONFIGURATION & SÉCURITÉ ---
TELEGRAM_TOKEN = "8149629372:AAGnAdf0QLNOHSBHNC5HYmvWuyoEqWJqEIo"
ADMIN_ID = "5220624399"
ADMIN_PASSWORD = "gold200512"
DB_FILE = "subscribers.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump([], f)

def get_subs():
    with open(DB_FILE, "r") as f: return json.load(f)

def diffuser(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_ID, "text": message, "parse_mode": "Markdown"})
    for sub in get_subs():
        requests.post(url, data={"chat_id": sub, "text": message, "parse_mode": "Markdown"})

# --- INIT PAGE & CSS ---
st.set_page_config(page_title="PREDATOR X TERMINAL", layout="wide", page_icon="🦅", initial_sidebar_state="expanded")

# INJECTION CSS (Le Design System)
st.markdown("""
<style>
    /* Fond général */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Cartes de Métriques (Custom Cards) */
    div.metric-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s;
    }
    div.metric-card:hover {
        transform: translateY(-5px);
        border-color: #F59E0B;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #F3F4F6;
    }
    .metric-label {
        font-size: 14px;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Boutons */
    div.stButton > button {
        background: linear-gradient(45deg, #F59E0B, #D97706);
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 10px #F59E0B;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #F59E0B;
    }
</style>
""", unsafe_allow_html=True)

# INIT SESSION
if "last_scan" not in st.session_state: st.session_state.last_scan = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5336/5336154.png", width=80)
    st.markdown("## 🦅 PREDATOR X")
    st.markdown("System V12 • Institutional")
    st.markdown("---")
    page = st.radio("NAVIGATION", ["Radar Stratégique", "Administration", "Journal des Logs"])
    st.markdown("---")
    tf = st.selectbox("TIMEFRAME", ["15m", "1h", "4h"])
    st.markdown("---")
    st.info("🟢 System: ONLINE\n\n📡 Feed: LIVE\n\n🛡️ Risk Manager: ACTIVE")

# --- FONCTION D'AFFICHAGE CARTE ---
def display_card(label, value, color="#F3F4F6"):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# --- PAGE: RADAR ---
if page == "Radar Stratégique":
    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("XAUUSD TERMINAL")
        st.caption("AI-Powered Institutional Trading System")
    with col_h2:
        if st.button("🔥 LANCER LE SCAN", use_container_width=True):
            with st.spinner('Synchronisation des flux institutionnels...'):
                df, sig, score, sl, tp, atr, imp, log, smc = get_ai_prediction(interval=tf)
                st.session_state.last_scan = {
                    "df": df, "sig": sig, "score": score, "sl": sl, "tp": tp, 
                    "atr": atr, "imp": imp, 
                    "p": df['Close'].iloc[-1] if df is not None else 0, 
                    "log": log, "smc": smc, "tf": tf
                }

    # Affichage Résultats
    if st.session_state.last_scan:
        res = st.session_state.last_scan
        
        # --- BLOC 1 : MARCHÉ FERMÉ ---
        if res['df'] is None:
            st.warning(f"💤 {res['sig']}")
            st.markdown("""
            <div style="background-color: #374151; padding: 20px; border-radius: 10px; text-align: center;">
                <h3>MARCHÉ FERMÉ</h3>
                <p>Le Forex (XAUUSD) est fermé le week-end.</p>
                <p>Le système est en veille active. Prochain scan : Dimanche 23h00.</p>
            </div>
            """, unsafe_allow_html=True)
            
        # --- BLOC 2 : MARCHÉ OUVERT ---
        else:
            # Code couleur dynamique
            color_sig = "#10B981" if "BUY" in res['sig'] else "#EF4444" if "SELL" in res['sig'] else "#F59E0B"
            
            # --- KPI ROW ---
            c1, c2, c3, c4 = st.columns(4)
            with c1: display_card("PRIX ACTUEL", f"{res['p']:.2f} $", "#F59E0B")
            with c2: display_card("SIGNAL IA", res['sig'].split(" ")[0], color_sig)
            with c3: display_card("SCORE CONFIANCE", f"{res['score']:.1f}%", color_sig)
            with c4: display_card("VOLATILITÉ (ATR)", f"{res['atr']:.2f}", "#9CA3AF")

            st.markdown("###") # Spacer

            # --- CONTEXTE ROW ---
            st.markdown("##### 🧠 ANALYSE CONTEXTUELLE")
            row1 = st.columns(3)
            # On parse le log qui est un dictionnaire ou string
            # Note: Assure-toi que get_ai_prediction renvoie bien un dict dans 'log' (V12)
            # Si c'est un string (V11), adapte ici. Supposons V12 dict.
            if isinstance(res['log'], dict):
                row1[0].info(f"**BIAS HTF** : {res['log'].get('htf', 'N/A')}")
                row1[1].info(f"**MACRO DXY** : {res['log'].get('dxy', 'N/A')}")
                row1[2].info(f"**STRUCTURE** : {res['log'].get('regime', 'N/A')}")
                
                if res['smc'] != 0:
                    st.error(f"💣 **SMC DETECTED** : {res['log'].get('smc', 'N/A')}")
            else:
                st.info(f"LOG: {res['log']}")

            st.markdown("---")

            # --- CHART & AI ROW ---
            col_chart, col_data = st.columns([2, 1])
            
            with col_chart:
                st.subheader("📈 Chart & Niveaux")
                fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
                
                # Ajout indicateurs stylés
                fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['EMA_200'], line=dict(color='#00E5FF', width=2), name='EMA 200'))
                fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['VWAP'], line=dict(color='#FFEA00', width=2), name='VWAP'))
                
                # Lignes TP/SL
                fig.add_hline(y=res['tp'], line_dash="dash", line_color="#10B981", annotation_text="TP", annotation_position="top right")
                fig.add_hline(y=res['sl'], line_dash="dash", line_color="#EF4444", annotation_text="SL", annotation_position="bottom right")

                fig.update_layout(
                    template="plotly_dark", 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=500,
                    margin=dict(l=0, r=0, t=30, b=0),
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_data:
                st.subheader("🎯 Plan d'Exécution")
                
                st.markdown(f"""
                <div style="background-color: #1F2937; padding: 15px; border-radius: 10px; border-left: 5px solid {color_sig};">
                    <p style="margin:0; color: #9CA3AF;">ENTRY PRICE</p>
                    <h2 style="margin:0; color: #F3F4F6;">{res['p']:.2f} $</h2>
                </div>
                <br>
                <div style="background-color: #1F2937; padding: 15px; border-radius: 10px; border-left: 5px solid #10B981;">
                    <p style="margin:0; color: #9CA3AF;">TAKE PROFIT</p>
                    <h2 style="margin:0; color: #10B981;">{res['tp']:.2f} $</h2>
                </div>
                <br>
                <div style="background-color: #1F2937; padding: 15px; border-radius: 10px; border-left: 5px solid #EF4444;">
                    <p style="margin:0; color: #9CA3AF;">STOP LOSS</p>
                    <h2 style="margin:0; color: #EF4444;">{res['sl']:.2f} $</h2>
                </div>
                <br>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 DIFFUSER CE SIGNAL", use_container_width=True):
                    # Reconstitution du message V12
                    rr_ratio = abs(res['tp'] - res['p']) / abs(res['p'] - res['sl']) if res['sl'] != 0 else 0
                    icon = "💎" if res['score'] >= 80 else "🔔"
                    
                    # Gestion compatibility V11/V12 pour le log
                    htf_txt = res['log'].get('htf', 'N/A') if isinstance(res['log'], dict) else "Analysis"
                    
                    msg = (f"{icon} *PREDATOR SIGNAL MANUAL*\n\n"
                           f"{res['sig']}\n"
                           f"📊 *Confidence*: {res['score']:.1f}%\n"
                           f"💵 *Price*: {res['p']:.2f}\n\n"
                           f"🏗️ *Context*: {htf_txt}\n"
                           f"⚖️ *R:R Ratio*: 1:{rr_ratio:.2f}\n"
                           f"✅ *TP*: {res['tp']:.2f}\n"
                           f"⛔ *SL*: {res['sl']:.2f}")
                    diffuser(msg)
                    st.toast("Signal diffusé à l'Empire !", icon="✅")

# --- PAGE: ADMIN ---
elif page == "Administration":
    st.title("🛡️ Zone Sécurisée")
    pwd = st.text_input("Mot de passe maître", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.success("Accès accordé.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 👥 Gestion Abonnés")
            new_id = st.text_input("Nouvel ID Telegram")
            if st.button("Ajouter Membre"):
                subs = get_subs()
                if new_id and new_id not in subs:
                    subs.append(new_id)
                    with open(DB_FILE, "w") as f: json.dump(subs, f)
                    st.success(f"ID {new_id} ajouté.")
                else:
                    st.warning("ID invalide ou déjà présent.")
            
            st.markdown("### Liste actuelle")
            st.code(get_subs())

        with c2:
            st.markdown("### ⚙️ État du Système")
            st.metric("Risk Manager", "ACTIF")
            st.metric("Auto Scanner", "EN COURS (PID: X)")
            st.markdown("Les logs systèmes sont disponibles dans la console serveur.")

# --- PAGE: LOGS ---
elif page == "Journal des Logs":
    st.title("📜 Journal des Trades")
    journal_file = "trading_journal.json"
    if os.path.exists(journal_file):
        with open(journal_file, "r") as f:
            data = json.load(f)
        if data:
            st.dataframe(data, use_container_width=True)
        else:
            st.info("Aucun trade enregistré pour le moment.")
    else:
        st.warning("Fichier journal introuvable.")