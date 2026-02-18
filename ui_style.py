import streamlit as st

# =========================================================
# 🔥 PREDATOR X - ULTIMATE CINEMATIC UI ENGINE V4.0
# =========================================================

def load_css():
    st.markdown("""
    <style>
        /* --- IMPORT FONTS PREMIUM --- */
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@300;500;700;900&family=Roboto+Mono:wght@300;500;700&display=swap');

        /* =======================================================
           🎨 GLOBAL THEME - ULTRA CINEMATIC
        ======================================================== */
        .stApp {
            background: #000000;
            background-image: 
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,215,0,0.03) 2px, rgba(255,215,0,0.03) 4px),
                repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255,215,0,0.03) 2px, rgba(255,215,0,0.03) 4px),
                radial-gradient(ellipse at 20% 30%, rgba(255,215,0,0.12) 0%, transparent 40%),
                radial-gradient(ellipse at 80% 70%, rgba(16, 185, 129, 0.12) 0%, transparent 40%);
            color: #e0e0e0;
            font-family: 'Rajdhani', sans-serif;
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: rgba(5, 5, 5, 0.95);
            border-right: 1px solid #333;
            backdrop-filter: blur(20px);
        }

        /* --- TITRES --- */
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif !important;
            text-transform: uppercase;
            letter-spacing: 3px;
        }

        /* --- METRIC CARDS (GLASSMORPHISM) --- */
        div.metric-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 15px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        div.metric-card:hover {
            border-color: rgba(255, 215, 0, 0.5);
            transform: translateY(-5px);
            box-shadow: 0 10px 30px -10px rgba(255, 215, 0, 0.15);
        }
        div.metric-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255,215,0,0.8), transparent);
            transform: translateX(-100%);
            transition: transform 0.5s;
        }
        div.metric-card:hover::before {
            transform: translateX(100%);
        }

        .metric-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 700;
            text-shadow: 0 0 20px rgba(0,0,0,0.5);
        }
        .metric-label {
            font-family: 'Roboto Mono', monospace;
            font-size: 10px;
            color: #666;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        .metric-icon {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 20px;
            opacity: 0.5;
        }

        /* --- ANIMATIONS --- */
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        @keyframes radar-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        @keyframes scanline {
            0% { top: -10%; opacity: 0; }
            50% { opacity: 1; }
            100% { top: 110%; opacity: 0; }
        }

        /* --- STANDBY SCREEN --- */
        .radar-container {
            position: relative;
            width: 300px;
            height: 300px;
            margin: 50px auto;
            border: 1px solid #333;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(10,10,10,1) 0%, rgba(0,0,0,1) 100%);
            box-shadow: 0 0 50px rgba(255, 215, 0, 0.1);
        }
        .radar-sweep {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            border-radius: 50%;
            background: conic-gradient(from 0deg, transparent 0deg, rgba(255, 215, 0, 0.1) 60deg, rgba(255, 215, 0, 0.4) 90deg, transparent 91deg);
            animation: radar-spin 4s linear infinite;
            border-right: 2px solid rgba(255, 215, 0, 0.8);
        }
        .radar-grid {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 80%; height: 80%;
            border: 1px dashed rgba(255, 255, 255, 0.1);
            border-radius: 50%;
        }

        /* --- BUTTONS --- */
        div.stButton > button {
            background: transparent;
            border: 1px solid #FFD700;
            color: #FFD700;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 2px;
            border-radius: 4px;
            transition: all 0.3s;
            text-transform: uppercase;
            width: 100%;
        }
        div.stButton > button:hover {
            background: #FFD700;
            color: #000;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.6);
            border-color: #FFD700;
        }

        /* --- SECTION TITLES --- */
        .section-title {
            font-family: 'Orbitron';
            font-size: 18px;
            color: #fff;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
            margin-bottom: 20px;
            margin-top: 30px;
            letter-spacing: 2px;
        }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# COMPOSANTS UI
# ---------------------------------------------------------

def render_header():
    """Affiche le header principal avec le statut système"""
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding: 20px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div>
                <h1 style="margin:0; font-size: 32px; background: linear-gradient(90deg, #FFD700, #FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PREDATOR X</h1>
                <div style="font-family: 'Roboto Mono'; font-size: 10px; color: #666; letter-spacing: 3px;">INSTITUTIONAL QUANTUM ENGINE // V12</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 8px; height: 8px; background: #10B981; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 10px #10B981; animation: pulse-green 2s infinite;"></div>
                <span style="font-family: 'Roboto Mono'; font-size: 12px; color: #10B981; font-weight: bold;">SYSTEM ONLINE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, sub_label, icon, color):
    """Affiche une carte de métrique style verre"""
    st.markdown(f"""
    <div class="metric-card" style="border-bottom: 2px solid {color};">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div style="font-size: 10px; color: #555; margin-top: 5px; font-family: 'Roboto Mono';">{sub_label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_standby_screen():
    """Affiche le radar animé quand le marché est fermé ou session inactive"""
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.timezone("Europe/Paris"))
    heure = now.strftime("%H:%M")
    heure_utc = datetime.now(pytz.utc).hour

    # Message dynamique selon l'heure
    if 0 <= heure_utc < 8:
        msg_status = "SESSION ASIATIQUE // FAIBLE VOLUME"
        msg_next = "SCAN ACTIF A 09:00 (HEURE DE PARIS)"
        couleur_next = "#FFD700"
    elif heure_utc >= 22 or (heure_utc == 21 and datetime.now(pytz.utc).minute >= 0):
        msg_status = "MARCHE FERME // FIN DE SESSION"
        msg_next = "PROCHAINE SESSION: DEMAIN 09:00"
        couleur_next = "#EF4444"
    else:
        msg_status = "MARKET CLOSED // PROTOCOL: SLEEP"
        msg_next = "PROCHAINE OUVERTURE: DIMANCHE 23:00 UTC"
        couleur_next = "#FFD700"

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
            <div style="text-align: center;">
                <div class="radar-container">
                    <div class="radar-grid"></div>
                    <div class="radar-sweep"></div>
                </div>
                <h2 style="color: #666; margin-top: 30px;">SYSTEM STANDBY</h2>
                <div style="font-family: 'Roboto Mono'; color: #444; font-size: 12px; margin-top: 10px;">
                    {msg_status}<br>
                    <span style="color: {couleur_next};">{msg_next}</span>
                </div>
                <div style="margin-top:15px; font-family:'Roboto Mono'; color:#333; font-size:11px;">
                    PARIS: {heure} &nbsp;|&nbsp; SCANNER: ACTIF
                </div>
            </div>
        """, unsafe_allow_html=True)

def render_sidebar_footer():
    """Footer dans la sidebar - version robuste sans emoji HTML"""
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.timezone("Europe/Paris"))
    heure = now.strftime("%H:%M")
    session = "Londres" if 9 <= now.hour < 17 else ("NY" if 14 <= now.hour < 22 else "Hors session")
    couleur_session = "#10B981" if now.hour >= 9 else "#F59E0B"

    st.sidebar.markdown(f"""
    <div style="margin-top:30px; padding:15px; background:rgba(255,255,255,0.02); border:1px solid rgba(255,215,0,0.15); border-radius:10px;">
        <div style="font-family:'Orbitron',sans-serif; font-size:10px; color:#FFD700; margin-bottom:12px; letter-spacing:2px;">SYSTEM STATUS</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:11px; color:#888;">Heure Paris</span>
            <span style="font-size:11px; color:#fff; font-family:'Roboto Mono',monospace;">{heure}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:11px; color:#888;">Session</span>
            <span style="font-size:11px; color:{couleur_session}; font-weight:bold;">{session}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="font-size:11px; color:#888;">Risk Manager</span>
            <span style="font-size:11px; color:#10B981;">OK</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="font-size:11px; color:#888;">Data Feed</span>
            <span style="font-size:11px; color:#10B981;">12ms</span>
        </div>
        <div style="margin-top:12px; height:1px; background:linear-gradient(90deg, transparent, rgba(255,215,0,0.4), transparent);"></div>
        <div style="margin-top:10px; font-size:9px; color:#444; text-align:center; font-family:'Roboto Mono',monospace;">PREDATOR V12 INSTITUTIONAL</div>
    </div>
    """, unsafe_allow_html=True)