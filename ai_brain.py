import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volume import VolumeWeightedAveragePrice
from datetime import datetime
import pytz

# MODULES EXPERTS
from market_regime import detect_market_regime
from smc_engine import detect_false_breakout 
from macro_data import analyze_macro_context
from htf_manager import analyze_htf_bias
from risk_manager import calculate_dynamic_risk, check_volatility_kill_switch, check_cooldown, log_trade

def check_market_open():
    now = datetime.now(pytz.utc)
    if now.weekday() == 5: return False, "WE (Samedi)"
    if now.weekday() == 4 and now.hour >= 22: return False, "Fermeture Hebdo"
    if now.weekday() == 6 and now.hour < 22: return False, "WE (Dimanche)"
    return True, "OUVERT"

def get_ai_prediction(interval="15m"):
    # 1. SÉCURITÉ MARCHÉ
    is_open, msg = check_market_open()
    if not is_open: return None, f"FERMÉ ({msg})", 0, 0, 0, 0, {}, msg, 0

    # 2. CHARGEMENT DATA
    try:
        gold = yf.Ticker("GC=F").history(period="5d", interval=interval)
        dxy = yf.Ticker("DX-Y.NYB").history(period="5d", interval="1h")
        if gold.empty: return None, "No Data", 0, 0, 0, 0, {}, "N/A", 0
    except: return None, "API Error", 0, 0, 0, 0, {}, "N/A", 0

    df = gold.copy()
    df['DXY'] = dxy['Close'].reindex(df.index, method='ffill').fillna(method='ffill')

    # --- CALCULS TECHNIQUES PRÉLIMINAIRES ---
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean() # ATR Simple
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
    df['EMA_200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
    try: df['VWAP'] = VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume']).volume_weighted_average_price()
    except: df['VWAP'] = df['EMA_200']

    # 3. VÉRIFICATIONS RISQUE (Kill Switch & Cooldown)
    kill_switch, kill_reason = check_volatility_kill_switch(df)
    if kill_switch:
        return df, "NEUTRE", 0, 0, 0, df['ATR'].iloc[-1], {}, f"⛔ {kill_reason}", 0

    can_trade, cooldown_msg = check_cooldown()
    if not can_trade:
        return df, "NEUTRE", 0, 0, 0, df['ATR'].iloc[-1], {}, f"⏳ {cooldown_msg}", 0

    # 4. ANALYSE DES EXPERTS
    bias_1, bias_2, score_htf, _, _ = analyze_htf_bias(interval) # HTF Bias
    regime_nom, regime_score, _, atr = detect_market_regime(df) # Regime
    smc_score, smc_raison = detect_false_breakout(df) # SMC / Fake Breakout
    macro_score, macro_raison = analyze_macro_context() # DXY / Yields

    # 5. IA TECHNIQUE (Machine Learning)
    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
    features = ['RSI', 'EMA_200', 'VWAP']
    model = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
    model.fit(df[features][:-1], df['Target'][:-1])
    pred_ia = model.predict(df[features].iloc[-1:])[0] # 1 = BUY, 0 = SELL

    # =========================================================
    # 🔥 1️⃣ SCORE DE CONFLUENCE MULTI-LAYER (Le Cœur V12)
    # =========================================================
    confidence_score = 0
    
    # A. Bias HTF (Structure de fond) - Max 30 pts
    # Règle : 5️⃣ MTF Structure Alignment
    if score_htf > 0 and pred_ia == 1: confidence_score += 25
    elif score_htf < 0 and pred_ia == 0: confidence_score += 25
    else: confidence_score -= 20 # Pénalité si on contre la tendance de fond

    # B. SMC & Fake Breakout (Timing) - Max 25 pts
    # Règle : 7️⃣ Fake Breakout Detector
    if smc_score > 0 and pred_ia == 1: confidence_score += 20
    elif smc_score < 0 and pred_ia == 0: confidence_score += 20

    # C. Macro & DXY (Filtre) - Max 20 pts
    # Règle : 6️⃣ DXY Confirmation
    if macro_score > 0 and pred_ia == 1: confidence_score += 15
    elif macro_score < 0 and pred_ia == 0: confidence_score += 15

    # D. Régime de Marché (Contexte) - Max 15 pts
    # Règle : 8️⃣ Regime Detector
    if "TREND" in regime_nom: confidence_score += 15
    elif "RANGE" in regime_nom and smc_score != 0: confidence_score += 10 # Bon pour SMC
    elif "EXPLOSION" in regime_nom: confidence_score -= 50 # Trop dangereux (Chaos)

    # E. IA Technique (Pattern) - Max 10 pts
    confidence_score += 10 # Base pour un signal technique propre

    # Bornage 0-100
    confidence_score = min(99.9, max(0.0, confidence_score))

    # 6. DÉCISION FINALE & GESTION RISQUE
    signal = "NEUTRE"
    direction_trade = None

    if confidence_score >= 80: 
        signal = "🟢 STRONG BUY"
        direction_trade = "BUY"
    elif confidence_score >= 60: 
        signal = "🟢 MODERATE BUY" if pred_ia == 1 else "🔴 MODERATE SELL"
        direction_trade = "BUY" if pred_ia == 1 else "SELL"
    elif confidence_score <= 20: # Fort signal vente
        signal = "🔴 STRONG SELL"
        direction_trade = "SELL"
    else:
        signal = "🟡 WAIT"

    # Calcul dynamique SL/TP (Si signal actif)
    sl, tp = 0, 0
    risk_msg = "N/A"
    
    if direction_trade:
        # Règle : 2️⃣ Dynamic Risk Engine
        sl, tp, risk_dist, risk_msg = calculate_dynamic_risk(df, direction_trade, atr)
        if sl is None: # Si R:R mauvais
            signal = "🟡 WAIT (R:R Invalid)"
            confidence_score = 0
        else:
            # Si on valide un trade, on le log
            if confidence_score >= 70:
                log_trade(direction_trade, df['Close'].iloc[-1], confidence_score, f"{smc_raison} | {macro_raison}", sl, tp)

    # Création du Log complet pour Telegram
    full_log = {
        "htf": "Bullish" if score_htf > 0 else "Bearish",
        "dxy": "Bearish" if macro_score > 0 else "Bullish", # Inverse
        "smc": smc_raison,
        "risk": risk_msg,
        "regime": regime_nom
    }

    return df, signal, confidence_score, sl, tp, atr, model.feature_importances_, full_log, smc_score