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
                radial-gradient(ellipse at 80% 70%, rgba(255,140,0,0.08) 0%, transparent 40%);
            background-size: 80px 80px, 80px 80px, 100% 100%, 100% 100%;
            font-family: 'Rajdhani', sans-serif;
            color: #E5E7EB;
            animation: gridFlow 30s linear infinite;
        }

        @keyframes gridFlow {
            0% { background-position: 0 0, 0 0, 0 0, 0 0; }
            100% { background-position: 80px 80px, 80px 80px, 0 0, 0 0; }
        }

        /* Particules flottantes */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20% 30%, rgba(255,215,0,0.3), transparent),
                radial-gradient(2px 2px at 60% 70%, rgba(255,215,0,0.2), transparent),
                radial-gradient(1px 1px at 50% 50%, rgba(255,215,0,0.25), transparent),
                radial-gradient(1px 1px at 80% 10%, rgba(255,215,0,0.2), transparent),
                radial-gradient(2px 2px at 90% 60%, rgba(255,215,0,0.15), transparent),
                radial-gradient(1px 1px at 33% 85%, rgba(255,215,0,0.2), transparent);
            background-size: 200% 200%;
            animation: particlesFloat 20s ease-in-out infinite;
            pointer-events: none;
            opacity: 0.4;
        }

        @keyframes particlesFloat {
            0%, 100% { 
                background-position: 0% 0%, 100% 100%, 50% 50%, 80% 20%, 10% 90%, 70% 30%;
                opacity: 0.3;
            }
            50% { 
                background-position: 100% 100%, 0% 0%, 80% 20%, 20% 80%, 90% 10%, 30% 70%;
                opacity: 0.5;
            }
        }

        /* =======================================================
           🧱 SIDEBAR ULTRA COMPACT & PREMIUM
        ======================================================== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(15,15,15,0.98) 0%, rgba(5,5,5,0.98) 100%);
            border-right: 2px solid rgba(255,215,0,0.4);
            backdrop-filter: blur(25px);
            box-shadow: 
                4px 0 40px rgba(255,215,0,0.15),
                inset -1px 0 30px rgba(255,215,0,0.05);
            position: relative;
        }

        /* Scanner vertical ULTRA */
        [data-testid="stSidebar"]::before {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 3px;
            height: 30%;
            background: linear-gradient(to bottom, 
                transparent, 
                rgba(255,215,0,1), 
                transparent);
            animation: scanVertical 2.5s ease-in-out infinite;
            filter: blur(1px);
            box-shadow: 0 0 15px rgba(255,215,0,0.8);
        }

        @keyframes scanVertical {
            0%, 100% { 
                top: -30%;
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                top: 100%;
                opacity: 0;
            }
        }

        /* Coins lumineux */
        [data-testid="stSidebar"]::after {
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: radial-gradient(circle at top right, rgba(255,215,0,0.2), transparent 70%);
            pointer-events: none;
            animation: cornerGlow 4s ease-in-out infinite;
        }

        @keyframes cornerGlow {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
        }

        /* Titre Sidebar ÉPIQUE */
        .sidebar-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 40%, #FFD700 60%, #FF8C00 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 15px;
            letter-spacing: 5px;
            position: relative;
            padding: 12px 0;
            animation: gradientShift 4s ease infinite, titlePulse 3s ease-in-out infinite;
            filter: drop-shadow(0 0 20px rgba(255,215,0,0.5));
        }

        @keyframes gradientShift {
            0%, 100% { background-position: 0% center; }
            50% { background-position: 100% center; }
        }

        @keyframes titlePulse {
            0%, 100% { 
                transform: scale(1);
                filter: drop-shadow(0 0 15px rgba(255,215,0,0.4));
            }
            50% { 
                transform: scale(1.03);
                filter: drop-shadow(0 0 30px rgba(255,215,0,0.7));
            }
        }

        .sidebar-title::after {
            content: "";
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            height: 3px;
            background: linear-gradient(90deg, transparent, #FFD700, transparent);
            animation: lineExpand 2s ease-in-out infinite;
            box-shadow: 0 0 10px rgba(255,215,0,0.8);
        }

        @keyframes lineExpand {
            0%, 100% { 
                width: 50%;
                opacity: 0.4;
            }
            50% { 
                width: 80%;
                opacity: 1;
            }
        }

        /* =======================================================
           📘 NAVIGATION - ONGLETS SPECTACULAIRES
        ======================================================== */
        div[role="radiogroup"] {
            gap: 10px;
            padding: 5px 0;
        }

        div[role="radiogroup"] label {
            padding: 14px 18px !important;
            border-radius: 12px !important;
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            border: 2px solid rgba(255,215,0,0.2) !important;
            background: linear-gradient(135deg, rgba(25,25,25,0.8), rgba(15,15,15,0.8)) !important;
            cursor: pointer !important;
            position: relative !important;
            overflow: hidden !important;
            backdrop-filter: blur(10px) !important;
        }

        /* Effet de lumière qui traverse */
        div[role="radiogroup"] label::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,215,0,0.4), 
                transparent);
            transition: left 0.6s ease;
        }

        div[role="radiogroup"] label:hover::before {
            left: 100%;
        }

        div[role="radiogroup"] label:hover {
            background: linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,140,0,0.1)) !important;
            border-color: rgba(255,215,0,0.6) !important;
            transform: translateX(8px) scale(1.03) !important;
            box-shadow: 
                0 8px 25px rgba(255,215,0,0.25),
                inset 0 0 20px rgba(255,215,0,0.1) !important;
        }

        /* Onglet sélectionné - ULTRA PREMIUM */
        div[role="radiogroup"] input:checked + div {
            background: linear-gradient(135deg, 
                rgba(255,215,0,0.3) 0%, 
                rgba(255,165,0,0.2) 50%,
                rgba(255,215,0,0.25) 100%) !important;
            border-left: 5px solid #FFD700 !important;
            border-color: rgba(255,215,0,0.8) !important;
            box-shadow: 
                0 0 40px rgba(255,215,0,0.4),
                inset 0 0 30px rgba(255,215,0,0.15),
                0 8px 30px rgba(255,215,0,0.2) !important;
            transform: translateX(6px) scale(1.02) !important;
            animation: selectedPulse 3s ease-in-out infinite !important;
        }

        @keyframes selectedPulse {
            0%, 100% { 
                box-shadow: 
                    0 0 30px rgba(255,215,0,0.3),
                    inset 0 0 25px rgba(255,215,0,0.12);
            }
            50% { 
                box-shadow: 
                    0 0 50px rgba(255,215,0,0.5),
                    inset 0 0 35px rgba(255,215,0,0.2);
            }
        }

        /* Indicateur animé */
        div[role="radiogroup"] input:checked + div::after {
            content: "▶";
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #FFD700;
            font-size: 12px;
            animation: arrowBounce 2s ease-in-out infinite;
            filter: drop-shadow(0 0 5px rgba(255,215,0,0.8));
        }

        @keyframes arrowBounce {
            0%, 100% { 
                transform: translateY(-50%) translateX(0);
                opacity: 0.6;
            }
            50% { 
                transform: translateY(-50%) translateX(4px);
                opacity: 1;
            }
        }

        /* =======================================================
           📊 SYSTEM STATUS BOX - COMPACT & ANIMATED
        ======================================================== */
        .status-box {
            background: linear-gradient(145deg, rgba(30,30,30,0.95), rgba(15,15,15,0.95));
            border: 2px solid rgba(255,215,0,0.4);
            border-radius: 14px;
            padding: 14px;
            margin-top: 20px;
            font-size: 12px;
            box-shadow: 
                0 8px 30px rgba(255,215,0,0.15),
                inset 0 1px 0 rgba(255,215,0,0.2);
            position: relative;
            overflow: hidden;
        }

        .status-box::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
                transparent, 
                rgba(255,215,0,0.15), 
                transparent);
            animation: statusSweep 4s ease-in-out infinite;
        }

        @keyframes statusSweep {
            0% { left: -100%; }
            50% { left: 100%; }
            100% { left: 100%; }
        }

        .status-dot {
            height: 14px;
            width: 14px;
            background: #10B981;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            position: relative;
            animation: statusDotPulse 2s ease-in-out infinite;
        }

        @keyframes statusDotPulse {
            0%, 100% { 
                box-shadow: 
                    0 0 0 0 rgba(16,185,129,0.7),
                    0 0 15px rgba(16,185,129,0.6);
                transform: scale(1);
            }
            50% { 
                box-shadow: 
                    0 0 0 8px rgba(16,185,129,0),
                    0 0 25px rgba(16,185,129,0.8);
                transform: scale(1.1);
            }
        }

        /* =======================================================
           📡 STANDBY SCREEN - MEGA CINEMATIC
        ======================================================== */
        .standby-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            border: 3px solid rgba(255,215,0,0.4);
            border-radius: 20px;
            background: 
                linear-gradient(145deg, rgba(20,20,20,0.98), rgba(10,10,10,0.98));
            position: relative;
            overflow: hidden;
            box-shadow: 
                0 0 60px rgba(255,215,0,0.2),
                inset 0 0 60px rgba(0,0,0,0.7);
            margin: 20px 0;
        }

        /* Background radar rotatif ultra */
        .standby-container::before {
            content: "";
            position: absolute;
            top: -100%;
            left: -100%;
            width: 300%;
            height: 300%;
            background: 
                repeating-conic-gradient(
                    from 0deg,
                    transparent 0deg 8deg,
                    rgba(255,215,0,0.03) 8deg 10deg
                );
            animation: megaRadarSpin 25s linear infinite;
        }

        @keyframes megaRadarSpin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* Cercles de scan pulsants */
        .standby-container::after {
            content: "";
            position: absolute;
            width: 400px;
            height: 400px;
            border: 2px solid rgba(255,215,0,0.2);
            border-radius: 50%;
            animation: scanPulse 4s ease-in-out infinite;
        }

        @keyframes scanPulse {
            0%, 100% { 
                transform: scale(0.8);
                opacity: 0;
            }
            50% { 
                transform: scale(1.2);
                opacity: 0.6;
            }
        }

        .radar-circle {
            width: 300px;
            height: 300px;
            border: 4px solid rgba(255,215,0,0.4);
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 40px;
            box-shadow: 
                0 0 50px rgba(255,215,0,0.3),
                inset 0 0 50px rgba(255,215,0,0.08);
            z-index: 10;
            animation: radarBreathing 4s ease-in-out infinite;
        }

        @keyframes radarBreathing {
            0%, 100% { 
                transform: scale(1);
                box-shadow: 
                    0 0 40px rgba(255,215,0,0.2),
                    inset 0 0 40px rgba(255,215,0,0.05);
            }
            50% { 
                transform: scale(1.05);
                box-shadow: 
                    0 0 60px rgba(255,215,0,0.4),
                    inset 0 0 60px rgba(255,215,0,0.12);
            }
        }

        /* Cercles concentriques */
        .radar-circle::before {
            content: "";
            position: absolute;
            width: 200px;
            height: 200px;
            border: 3px solid rgba(255,215,0,0.3);
            border-radius: 50%;
            animation: innerPulse 3s ease-in-out infinite;
        }

        @keyframes innerPulse {
            0%, 100% { 
                transform: scale(1);
                opacity: 0.4;
            }
            50% { 
                transform: scale(1.1);
                opacity: 0.7;
            }
        }

        .radar-circle::after {
            content: "";
            position: absolute;
            width: 100px;
            height: 100px;
            border: 2px solid rgba(255,215,0,0.25);
            border-radius: 50%;
            animation: innerPulse 3s ease-in-out infinite 0.5s;
        }

        .radar-line {
            width: 150px;
            height: 4px;
            background: linear-gradient(90deg, 
                rgba(255,215,0,1), 
                rgba(255,215,0,0.6),
                transparent);
            position: absolute;
            top: 50%;
            left: 50%;
            transform-origin: 0% 50%;
            animation: radarSpin 3s linear infinite;
            box-shadow: 0 0 25px rgba(255,215,0,0.8);
            filter: blur(0.5px);
        }

        @keyframes radarSpin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .radar-dot {
            width: 18px;
            height: 18px;
            background: #FFD700;
            border-radius: 50%;
            box-shadow: 
                0 0 30px #FFD700,
                0 0 60px rgba(255,215,0,0.6),
                0 0 90px rgba(255,215,0,0.3);
            animation: dotMegaPulse 2s ease-in-out infinite;
            z-index: 20;
        }

        @keyframes dotMegaPulse {
            0%, 100% { 
                transform: scale(1);
                box-shadow: 
                    0 0 25px #FFD700,
                    0 0 50px rgba(255,215,0,0.5);
            }
            50% { 
                transform: scale(1.4);
                box-shadow: 
                    0 0 40px #FFD700,
                    0 0 80px rgba(255,215,0,0.7),
                    0 0 120px rgba(255,215,0,0.4);
            }
        }

        .standby-text {
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            font-weight: 900;
            background: linear-gradient(90deg, #666, #FFD700, #FFA500, #FFD700, #666);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 6px;
            text-transform: uppercase;
            animation: textFlow 4s linear infinite;
            z-index: 10;
            filter: drop-shadow(0 0 20px rgba(255,215,0,0.5));
        }

        @keyframes textFlow {
            0% { background-position: 0% center; }
            100% { background-position: 200% center; }
        }

        .standby-sub {
            font-family: 'Rajdhani', sans-serif;
            font-size: 15px;
            color: #AAA;
            margin-top: 15px;
            letter-spacing: 3px;
            z-index: 10;
            animation: subTextPulse 3s ease-in-out infinite;
        }

        @keyframes subTextPulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }

        /* =======================================================
           🚀 MAIN HEADER
        ======================================================== */
        h1 {
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 900 !important;
            font-size: 52px !important;
            letter-spacing: 6px !important;
            background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700) !important;
            background-size: 200% auto !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            animation: titleFlow 3s ease infinite !important;
            filter: drop-shadow(0 0 30px rgba(255,215,0,0.6)) !important;
            margin-bottom: 10px !important;
        }

        @keyframes titleFlow {
            0%, 100% { background-position: 0% center; }
            50% { background-position: 100% center; }
        }

        /* =======================================================
           🔥 BOUTONS - ULTRA GLOW
        ======================================================== */
        div.stButton > button {
            background: transparent !important;
            border: 3px solid #FFD700 !important;
            color: #FFD700 !important;
            font-family: 'Orbitron', sans-serif !important;
            font-weight: 800 !important;
            border-radius: 10px !important;
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
            text-transform: uppercase !important;
            letter-spacing: 3px !important;
            padding: 14px 28px !important;
            position: relative !important;
            overflow: hidden !important;
        }

        div.stButton > button::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: radial-gradient(circle, rgba(255,215,0,0.3), transparent 70%);
            transform: translate(-50%, -50%);
            transition: width 0.6s ease, height 0.6s ease;
        }

        div.stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #FFD700, #FFA500) !important;
            color: #000000 !important;
            box-shadow: 
                0 0 40px rgba(255,215,0,0.7),
                0 0 80px rgba(255,215,0,0.4),
                inset 0 0 30px rgba(255,255,255,0.3) !important;
            transform: translateY(-3px) scale(1.05) !important;
            border-color: #FFD700 !important;
        }

        /* =======================================================
           📊 AUTRES ÉLÉMENTS
        ======================================================== */
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(30,30,30,0.9), rgba(20,20,20,0.9)) !important;
            padding: 18px !important;
            border-radius: 14px !important;
            border: 2px solid rgba(255,215,0,0.3) !important;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6) !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-6px);
            border-color: rgba(255,215,0,0.6) !important;
            box-shadow: 0 12px 40px rgba(255,215,0,0.3) !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 36px !important;
            font-weight: 800 !important;
            color: #FFD700 !important;
            font-family: 'Rajdhani', sans-serif !important;
        }

        div[data-baseweb="select"] > div {
            background: rgba(30,30,30,0.95) !important;
            border: 2px solid rgba(255,215,0,0.4) !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
        }

        div[data-baseweb="select"] > div:hover {
            border-color: #FFD700 !important;
            box-shadow: 0 0 20px rgba(255,215,0,0.3) !important;
        }

        input {
            background: rgba(30,30,30,0.95) !important;
            border: 2px solid rgba(255,215,0,0.4) !important;
            border-radius: 10px !important;
            color: white !important;
            transition: all 0.3s ease !important;
        }

        input:focus {
            border-color: #FFD700 !important;
            box-shadow: 0 0 20px rgba(255,215,0,0.4) !important;
        }

        .stSuccess {
            background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(5,150,105,0.25)) !important;
            border-left: 5px solid #10B981 !important;
            border-radius: 10px !important;
        }

        ::-webkit-scrollbar {
            width: 12px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(20,20,20,0.6);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #FFD700, #FFA500);
            border-radius: 6px;
            border: 2px solid rgba(0,0,0,0.3);
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(180deg, #FFA500, #FF8C00);
        }

    </style>
    """, unsafe_allow_html=True)


def render_sidebar_header():
    st.sidebar.markdown('<div class="sidebar-title">🦅 PREDATOR X</div>', unsafe_allow_html=True)


def render_system_status():
    st.sidebar.markdown("""
    <div class="status-box">
        <div style="display:flex; align-items:center; margin-bottom:10px; position:relative; z-index:10;">
            <div class="status-dot"></div>
            <span style="color:#10B981; font-weight:800; font-family:'Rajdhani', sans-serif; font-size:14px; letter-spacing:1px; text-transform:uppercase;">System Online</span>
        </div>
        <div style="position:relative; z-index:10; font-family:'Rajdhani', sans-serif; font-size:13px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="color:#AAA;">🖥️ Server:</span>
                <span style="color:#FFD700; font-weight:700;">GCP-E2</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span style="color:#AAA;">⚡ Latency:</span>
                <span style="color:#10B981; font-weight:700;">12ms</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#AAA;">🔧 Module:</span>
                <span style="color:#FFD700; font-weight:700;">V12 INST</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_standby_screen():
    """Écran de veille ULTRA CINEMATIC"""
    st.markdown("""
    <div class="standby-container">
        <div class="radar-circle">
            <div class="radar-line"></div>
            <div class="radar-dot"></div>
        </div>
        <div class="standby-text">System Standby</div>
        <div class="standby-sub">MARCHÉ FERMÉ • PROTOCOLE DE VEILLE ACTIF</div>
        <div style="margin-top: 30px; font-size: 12px; color: #666; font-family:'Roboto Mono', monospace; position:relative; z-index:10; letter-spacing:2px;">
            🔒 AWAITING MARKET OPENING SIGNAL
        </div>
    </div>
    """, unsafe_allow_html=True)