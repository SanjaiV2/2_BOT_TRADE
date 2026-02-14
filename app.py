import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests
import json
import os
from ai_brain import get_ai_prediction

# CONFIG
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

# INIT SESSION
if "last_scan" not in st.session_state: st.session_state.last_scan = None

st.set_page_config(page_title="PREDATOR X INSTITUTIONAL", layout="wide", page_icon="🦅")

st.sidebar.title("🦅 PREDATOR X")
page = st.sidebar.radio("Menu", ["Radar Stratégique", "Admin"])
tf = st.sidebar.selectbox("Timeframe", ["15m", "1h", "4h"])

if page == "Radar Stratégique":
    st.title("🛡️ Radar Quantitatif (Institutionnel)")
    
    if st.button("🔥 LANCER LE SCAN INTELLIGENT", type="primary"):
        with st.spinner('Analyse Régime + SMC + Macro...'):
            # On récupère les 9 variables
            df, sig, score, sl, tp, atr, imp, log, smc = get_ai_prediction(interval=tf)
            
            # On stocke tout, même si df est None (cas du Week-End)
            st.session_state.last_scan = {
                "df": df, "sig": sig, "score": score, "sl": sl, "tp": tp, 
                "atr": atr, "imp": imp, 
                "p": df['Close'].iloc[-1] if df is not None else 0, 
                "log": log, "smc": smc, "tf": tf
            }

    # AFFICHAGE DES RÉSULTATS
    if st.session_state.last_scan:
        res = st.session_state.last_scan
        
        # CAS 1 : MARCHÉ FERMÉ (Week-End)
        if res['df'] is None:
            st.warning(f"💤 {res['sig']}") # Affiche "MARCHÉ FERMÉ"
            st.info("Le marché de l'Or (XAUUSD) est fermé le week-end. Le bot se repose pour éviter les faux signaux. Reprise Dimanche soir (Session Asie).")
            st.image("https://media.giphy.com/media/l0HlHFRbmaZtBRhXG/giphy.gif", width=300) # Petit GIF de repos (optionnel)
            
        # CAS 2 : MARCHÉ OUVERT
        else:
            # INFO CONTEXTE
            st.markdown(f"### 🌍 Contexte : {res['log']}")
            
            # METRICS
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Prix", f"{res['p']:.2f} $")
            c2.metric("Décision", res['sig'])
            c3.metric("Score Global", f"{res['score']:.1f} / 100")
            c4.metric("Volatilité", f"{res['atr']:.2f}")

            # BARRE DE PROGRESSION
            st.progress(int(res['score']))

            # MESSAGE SMC (Smart Money)
            if res['smc'] != 0:
                type_smc = "🟢 BULLISH SWEEP (Achat Smart Money)" if res['smc'] == 1 else "🔴 BEARISH SWEEP (Vente Smart Money)"
                st.error(f"💣 **ALERTE SMC DÉTECTÉE :** {type_smc}")

            # ACTIONS
            st.markdown("---")
            col_plan, col_act = st.columns([2, 1])
            with col_plan:
                st.info(f"📍 **PLAN :** Entrée {res['p']:.2f} | **TP {res['tp']:.2f}** | SL {res['sl']:.2f}")
            with col_act:
                if st.button("📢 DIFFUSER CE SIGNAL"):
                    msg = (f"🦅 *PREDATOR X (SMC)*\n\n"
                           f"🌍 *Log* : {res['log']}\n"
                           f"🎯 *Action* : {res['sig']}\n"
                           f"💯 *Score* : {res['score']:.1f}/100\n"
                           f"💵 *Prix* : {res['p']:.2f}\n"
                           f"✅ *TP* : {res['tp']:.2f}\n⛔ *SL* : {res['sl']:.2f}")
                    diffuser(msg)
                    st.success("Signal Envoyé !")

            # CHART
            st.markdown("---")
            fig = go.Figure(data=[go.Candlestick(x=res['df'].index, open=res['df']['Open'], high=res['df']['High'], low=res['df']['Low'], close=res['df']['Close'])])
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['EMA_200'], line=dict(color='cyan'), name='EMA 200'))
            fig.add_trace(go.Scatter(x=res['df'].index, y=res['df']['VWAP'], line=dict(color='orange'), name='VWAP'))
            fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

elif page == "Admin":
    st.title("🔑 Administration")
    pwd = st.text_input("Mot de passe", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("Accès autorisé.")
        new_id = st.text_input("Ajouter ID Telegram")
        if st.button("Ajouter"):
            subs = get_subs()
            if new_id not in subs:
                subs.append(new_id)
                with open(DB_FILE, "w") as f: json.dump(subs, f)
                st.success("Ajouté !")
        st.write("Abonnés :", get_subs())