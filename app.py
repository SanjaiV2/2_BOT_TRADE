import streamlit as st
import json
import os
import requests
from ai_brain import get_ai_prediction
import ui_style as ui  # <--- On importe notre nouveau fichier de style

# CONFIG & CONSTANTES
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

# --- INIT PAGE ---
st.set_page_config(page_title="PREDATOR X TERMINAL", layout="wide", page_icon="🦅")

# ON CHARGE LE STYLE FUTURISTE
ui.load_css()

# INIT SESSION
if "last_scan" not in st.session_state: st.session_state.last_scan = None

# --- SIDEBAR (Nouvelle Version) ---
ui.render_sidebar_header()

st.sidebar.markdown("### NAVIGATION")
page = st.sidebar.radio("", ["RADAR STRATEGIQUE", "ADMINISTRATION", "JOURNAL DES LOGS"])

st.sidebar.markdown("---")
st.sidebar.markdown("### PARAMÈTRES")
tf = st.sidebar.selectbox("TIMEFRAME", ["15m", "1h", "4h"])

ui.render_system_status() # Le petit bloc avec le point vert qui clignote

# --- PAGE: RADAR ---
if page == "RADAR STRATEGIQUE":
    st.title("XAUUSD // TERMINAL")
    
    # Bouton de scan
    if st.button("INITIALISER LE SCAN", use_container_width=True):
        with st.spinner('Accessing Institutional Data Feeds...'):
            df, sig, score, sl, tp, atr, imp, log, smc = get_ai_prediction(interval=tf)
            st.session_state.last_scan = {
                "df": df, "sig": sig, "score": score, "sl": sl, "tp": tp, 
                "atr": atr, "imp": imp, 
                "p": df['Close'].iloc[-1] if df is not None else 0, 
                "log": log, "smc": smc, "tf": tf
            }

    # Résultats
    if st.session_state.last_scan:
        res = st.session_state.last_scan
        
        # CAS 1 : MARCHÉ FERMÉ (Écran Stylé)
        if res['df'] is None:
            ui.render_standby_screen() # <--- Appel de l'écran radar animé
            
        # CAS 2 : MARCHÉ OUVERT (Affichage classique Dashboard)
        else:
            # (Je garde le code d'affichage classique ici pour quand ça ouvrira)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("PRIX", f"{res['p']:.2f} $")
            c2.metric("SIGNAL", res['sig'])
            c3.metric("SCORE", f"{res['score']:.1f}%")
            c4.metric("VOLATILITÉ", f"{res['atr']:.2f}")
            
            st.markdown("---")
            st.info(f"PLAN DE BATAILLE : TP {res['tp']} | SL {res['sl']}")
            
            if st.button("DIFFUSER SIGNAL"):
                diffuser(f"🦅 PREDATOR SIGNAL: {res['sig']}")
                st.success("Envoyé.")

# --- PAGE: ADMIN ---
elif page == "ADMINISTRATION":
    st.markdown("## 🛡️ ZONE SÉCURISÉE")
    pwd = st.text_input("PASSWORD", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("ACCESS GRANTED")
        st.write("Abonnés:", get_subs())
        new_id = st.text_input("Add Telegram ID")
        if st.button("ADD USER"):
            subs = get_subs()
            subs.append(new_id)
            with open(DB_FILE, "w") as f: json.dump(subs, f)
            st.success("User Added.")

# --- PAGE: LOGS ---
elif page == "JOURNAL DES LOGS":
    st.markdown("## 📜 BLACK BOX LOGS")
    if os.path.exists("trading_journal.json"):
        with open("trading_journal.json", "r") as f:
            st.dataframe(json.load(f), use_container_width=True)
    else:
        st.warning("NO DATA FOUND.")