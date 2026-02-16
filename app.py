import streamlit as st
import json
import os
import requests
import plotly.graph_objects as go
from ai_brain import get_ai_prediction
import ui_style as ui

# --- CONFIGURATION DU BOT ---
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

# --- INITIALISATION DE LA PAGE ---
st.set_page_config(page_title="PREDATOR X // ULTIMATE", layout="wide", page_icon="🦅")
ui.load_css()

if "last_scan" not in st.session_state: st.session_state.last_scan = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-family: 'Orbitron'; font-size: 24px; color: #FFD700; letter-spacing: 3px; text-shadow: 0 0 10px #FFD700;">
                PREDATOR<span style="color:#fff">X</span>
            </div>
            <div style="font-size: 10px; color: #666; letter-spacing: 2px;">INSTITUTIONAL AI</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    page = st.radio("NAVIGATION", ["RADAR STRATEGIQUE", "ADMINISTRATION", "BLACK BOX LOGS"])
    st.markdown("---")
    st.markdown("### ⚙️ PARAMÈTRES")
    tf = st.selectbox("TIMEFRAME", ["15m", "1h", "4h"])
    ui.render_sidebar_footer()

# --- PAGE PRINCIPALE ---
ui.render_header()

if page == "RADAR STRATEGIQUE":
    if st.button("⚡ INITIALISER LE SCAN SYSTÈME", use_container_width=True):
        with st.spinner('Accessing Institutional Data Feeds...'):
            df, sig, score, sl, tp, atr, imp, log, smc = get_ai_prediction(interval=tf)
            st.session_state.last_scan = {
                "df": df, "sig": sig, "score": score, "sl": sl, "tp": tp, 
                "atr": atr, "imp": imp, 
                "p": df['Close'].iloc[-1] if df is not None else 0, 
                "log": log, "smc": smc, "tf": tf
            }

    if st.session_state.last_scan:
        res = st.session_state.last_scan
        
        if res['df'] is None:
            ui.render_standby_screen()
            
        else:
            c1, c2, c3, c4 = st.columns(4)
            color_sig = "#10B981" if "BUY" in res['sig'] else "#EF4444" if "SELL" in res['sig'] else "#F59E0B"
            icon_sig = "🚀" if "BUY" in res['sig'] else "🔻" if "SELL" in res['sig'] else "⚠️"

            with c1: ui.render_metric_card("PRIX EN DIRECT", f"{res['p']:.2f} $", "XAUUSD", "💲", "#FFD700")
            with c2: ui.render_metric_card("SIGNAL IA", res['sig'].split(" ")[0], res['sig'], icon_sig, color_sig)
            with c3: ui.render_metric_card("SCORE CONFIANCE", f"{res['score']:.1f}%", "PROBABILITY", "🎯", "#3B82F6")
            with c4: ui.render_metric_card("VOLATILITÉ", f"{res['atr']:.2f}", "ATR LEVEL", "🌊", "#A855F7")

            st.markdown("<br>", unsafe_allow_html=True)

            col_chart, col_plan = st.columns([2, 1])
            with col_chart:
                st.markdown('<div class="section-title">📡 ANALYSE TECHNIQUE & CONTEXTE</div>', unsafe_allow_html=True)
                fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
                fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['EMA_200'], line=dict(color='#00E5FF', width=2), name='EMA 200'))
                fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['VWAP'], line=dict(color='#FFD700', width=2), name='VWAP'))
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, margin=dict(l=0, r=0, t=20, b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                st.info(f"🧬 **LOGIC MATRIX:** {res['log']}")

            with col_plan:
                st.markdown('<div class="section-title">🎯 EXECUTION PLAN</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                    <div style="color: #10B981; font-size: 12px; font-weight: bold;">TAKE PROFIT (TP)</div>
                    <div style="color: #fff; font-size: 24px; font-weight: bold; font-family: 'Rajdhani';">{res['tp']:.2f} $</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                    <div style="color: #EF4444; font-size: 12px; font-weight: bold;">STOP LOSS (SL)</div>
                    <div style="color: #fff; font-size: 24px; font-weight: bold; font-family: 'Rajdhani';">{res['sl']:.2f} $</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📢 DIFFUSER CE SIGNAL", use_container_width=True):
                    # --- RESTAURATION DU FORMAT VISUEL ---
                    msg = (f"🦅 *PREDATOR ALERTE - XAUUSD* 🦅\n\n"
                           f"⏱️ *Timeframe* : {res['tf'].upper()}\n"
                           f"🎯 *Action* : {res['sig']}\n"
                           f"📈 *Confiance* : {res['score']:.1f}%\n"
                           f"💵 *Prix actuel* : {res['p']:.2f} $\n\n"
                           f"✅ *TP* : {res['tp']:.2f} $\n"
                           f"⛔ *SL* : {res['sl']:.2f} $")
                    diffuser(msg)
                    st.toast("Signal diffusé au réseau crypté.", icon="✅")

elif page == "ADMINISTRATION":
    st.markdown('<div class="section-title">🛡️ ZONE SÉCURISÉE</div>', unsafe_allow_html=True)
    pwd = st.text_input("MOT DE PASSE MAÎTRE", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("AUTHENTIFICATION RÉUSSIE")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 👥 GESTION ABONNÉS")
            new_id = st.text_input("Ajouter ID Telegram")
            if st.button("VALIDER ACCÈS"):
                subs = get_subs()
                if new_id and new_id not in subs:
                    subs.append(new_id)
                    with open(DB_FILE, "w") as f: json.dump(subs, f)
                    st.success(f"Utilisateur {new_id} ajouté.")
        with c2:
            st.markdown("### 📜 LISTE ACTUELLE")
            st.code(get_subs())

elif page == "BLACK BOX LOGS":
    st.markdown('<div class="section-title">📜 JOURNAL DES TRADES</div>', unsafe_allow_html=True)
    if os.path.exists("trading_journal.json"):
        with open("trading_journal.json", "r") as f:
            st.dataframe(json.load(f), use_container_width=True)
    else:
        st.warning("AUCUNE DONNÉE ENREGISTRÉE.")