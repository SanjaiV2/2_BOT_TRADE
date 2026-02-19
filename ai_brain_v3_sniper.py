import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import EMAIndicator, MACD
from ta.volume import VolumeWeightedAveragePrice
from datetime import datetime
import pytz

# MODULES EXPERTS
from market_regime import detect_market_regime
from smc_engine import detect_false_breakout 
from macro_data import analyze_macro_context
from htf_manager import analyze_htf_bias
from risk_manager import calculate_dynamic_risk, check_volatility_kill_switch, check_cooldown, log_trade
from structure_analysis import analyze_institutional_structure  # 🆕 MODULE SNIPER

def check_market_open():
    now = datetime.now(pytz.utc)
    if now.weekday() == 5: return False, "WE (Samedi)"
    if now.weekday() == 4 and now.hour >= 22: return False, "Fermeture Hebdo"
    if now.weekday() == 6 and now.hour < 22: return False, "WE (Dimanche)"
    return True, "OUVERT"

def check_trading_session():
    """Filtre de session - Trade uniquement Londres/NY"""
    now = datetime.now(pytz.utc)
    hour = now.hour
    
    if 0 <= hour < 8:
        return False, "Session Asiatique"
    elif 8 <= hour < 16:
        return True, "Londres"
    elif 13 <= hour < 21:
        return True, "NY" 
    else:
        return False, "Hors Session"

def check_session_volume_quality(df):
    """
    🆕 FILTRE QUALITÉ DE SESSION
    Vérifie que le volume est suffisant pour trader
    """
    current_volume = df['Volume'].iloc[-1]
    avg_volume_20 = df['Volume'].rolling(20).mean().iloc[-1]
    avg_volume_50 = df['Volume'].rolling(50).mean().iloc[-1]
    
    # Volume doit être au moins 80% de la moyenne
    if current_volume < (avg_volume_20 * 0.8):
        return False, "Volume faible (< 80% moyenne)"
    
    # Tendance de volume (en augmentation = bon)
    if avg_volume_20 > avg_volume_50 * 1.1:
        return True, "Volume fort (tendance hausse)"
    
    return True, "Volume acceptable"

def check_momentum_confirmation(df):
    """Filtre de momentum"""
    rsi = df['RSI'].iloc[-1]
    stoch = StochasticOscillator(df['High'], df['Low'], df['Close'], window=14, smooth_window=3).stoch().iloc[-1]
    macd_obj = MACD(df['Close'])
    macd_diff = macd_obj.macd_diff().iloc[-1]
    vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    
    momentum_score = 0
    reasons = []
    
    # BUY momentum
    if rsi > 50 and rsi < 70:
        momentum_score += 15
        reasons.append("RSI Bullish")
    if stoch > 50 and stoch < 80:
        momentum_score += 10
        reasons.append("Stoch Bullish")
    if macd_diff > 0:
        momentum_score += 15
        reasons.append("MACD+")
    if vol_ratio > 1.2:
        momentum_score += 10
        reasons.append("Volume↑")
    
    # SELL momentum
    sell_momentum = 0
    sell_reasons = []
    if rsi < 50 and rsi > 30:
        sell_momentum += 15
        sell_reasons.append("RSI Bearish")
    if stoch < 50 and stoch > 20:
        sell_momentum += 10
        sell_reasons.append("Stoch Bearish")
    if macd_diff < 0:
        sell_momentum += 15
        sell_reasons.append("MACD-")
    if vol_ratio > 1.2:
        sell_momentum += 10
        sell_reasons.append("Volume↑")
    
    if momentum_score > sell_momentum:
        return "BUY", momentum_score, " | ".join(reasons)
    elif sell_momentum > momentum_score:
        return "SELL", sell_momentum, " | ".join(sell_reasons)
    else:
        return "NEUTRAL", 0, "Pas de momentum"

def get_ai_prediction(interval="1h"):
    # 1. SÉCURITÉ MARCHÉ
    is_open, msg = check_market_open()
    if not is_open: 
        return None, f"FERMÉ ({msg})", 0, 0, 0, 0, {}, msg, 0

    # 2. VÉRIFICATION SESSION
    good_session, session_msg = check_trading_session()
    if not good_session:
        return None, f"ATTENTE ({session_msg})", 0, 0, 0, 0, {}, session_msg, 0

    # 3. CHARGEMENT DATA
    try:
        gold = yf.Ticker("GC=F").history(period="10d", interval=interval)  # Plus de données pour structure
        dxy = yf.Ticker("DX-Y.NYB").history(period="5d", interval="1h")
        if gold.empty or len(gold) < 100:
            return None, "Données insuffisantes", 0, 0, 0, 0, {}, "N/A", 0
    except:
        return None, "API Error", 0, 0, 0, 0, {}, "N/A", 0

    df = gold.copy()
    df['DXY'] = dxy['Close'].reindex(df.index, method='ffill').fillna(method='ffill')

    # CALCULS TECHNIQUES
    df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
    df['EMA_50'] = EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA_200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
    try: 
        df['VWAP'] = VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume']).volume_weighted_average_price()
    except: 
        df['VWAP'] = df['EMA_200']

    # 4. VÉRIFICATIONS RISQUE
    kill_switch, kill_reason = check_volatility_kill_switch(df)
    if kill_switch:
        return df, "NEUTRE", 0, 0, 0, df['ATR'].iloc[-1], {}, f"⛔ {kill_reason}", 0

    can_trade, cooldown_msg = check_cooldown()
    if not can_trade:
        return df, "NEUTRE", 0, 0, 0, df['ATR'].iloc[-1], {}, f"⏳ {cooldown_msg}", 0

    # 🆕 5. VÉRIFICATION QUALITÉ VOLUME SESSION
    volume_ok, volume_msg = check_session_volume_quality(df)
    if not volume_ok:
        return df, "NEUTRE (Volume faible)", 0, 0, 0, df['ATR'].iloc[-1], {}, volume_msg, 0

    # 6. MOMENTUM
    momentum_dir, momentum_score, momentum_reason = check_momentum_confirmation(df)
    if momentum_score < 35:  # Seuil relevé : 35 au lieu de 30
        return df, "NEUTRE (Momentum faible)", 0, 0, 0, df['ATR'].iloc[-1], {}, momentum_reason, 0

    # 🆕 7. ANALYSE STRUCTURE INSTITUTIONNELLE (LE FILTRE SNIPER)
    structure_score, structure_bias, structure_log = analyze_institutional_structure(df)
    
    # ⚠️ FILTRES STRICTS STRUCTURE
    fib_zone = structure_log['fib_zone']
    bos_type = structure_log['bos']
    
    # RÈGLE 1 : On ne trade PAS en EQUILIBRIUM (zone mid-range)
    if "EQUILIBRIUM" in fib_zone:
        return df, "NEUTRE (Zone Equilibrium)", 0, 0, 0, df['ATR'].iloc[-1], {}, \
               f"🚫 Prix en zone {fib_zone} (mid-range interdit)", 0
    
    # RÈGLE 2 : BUY uniquement en DISCOUNT | SELL uniquement en PREMIUM
    if momentum_dir == "BUY" and "PREMIUM" in fib_zone:
        return df, "NEUTRE (BUY en Premium)", 0, 0, 0, df['ATR'].iloc[-1], {}, \
               f"🚫 BUY impossible en {fib_zone}", 0
    
    if momentum_dir == "SELL" and "DISCOUNT" in fib_zone:
        return df, "NEUTRE (SELL en Discount)", 0, 0, 0, df['ATR'].iloc[-1], {}, \
               f"🚫 SELL impossible en {fib_zone}", 0
    
    # RÈGLE 3 : Break of Structure OBLIGATOIRE pour signaux forts
    # (On accepte sans BOS seulement si score structure très élevé)
    bos_required = structure_score < 25  # Si score < 25, on exige BOS
    if bos_required and "NONE" in bos_type:
        return df, "NEUTRE (Pas de BOS)", 0, 0, 0, df['ATR'].iloc[-1], {}, \
               "🚫 Break of Structure requis", 0

    # 8. ANALYSE EXPERTS CLASSIQUES
    bias_1, bias_2, score_htf, _, _ = analyze_htf_bias(interval)
    regime_nom, regime_score, _, atr = detect_market_regime(df)
    smc_score, smc_raison = detect_false_breakout(df)
    macro_score, macro_raison = analyze_macro_context()

    # 9. IA TECHNIQUE
    df['Target'] = np.where(df['Close'] > df['Close'].shift(1), 1, 0)
    features = ['RSI', 'EMA_50', 'EMA_200', 'VWAP']
    
    if len(df) < 250:
        return df, "NEUTRE (Historique insuffisant)", 0, 0, 0, atr, {}, "N/A", 0
    
    train_data = df[features].iloc[:-1].fillna(method='ffill')
    train_target = df['Target'].iloc[:-1]
    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, min_samples_split=10)
    model.fit(train_data, train_target)
    current_features = df[features].iloc[-1:].fillna(method='ffill')
    pred_ia = model.predict(current_features)[0]

    # =========================================================
    # 🎯 SCORE DE CONFLUENCE V3 SNIPER (ULTRA STRICT)
    # =========================================================
    confidence_score = 0
    penalties = 0
    
    # A. STRUCTURE INSTITUTIONNELLE (NOUVEAU - POIDS MAXIMUM)
    if structure_score > 30:
        confidence_score += 40  # Poids énorme
    elif structure_score > 20:
        confidence_score += 30
    elif structure_score > 10:
        confidence_score += 20
    elif structure_score < -30:
        confidence_score += 40  # Bearish
    elif structure_score < -20:
        confidence_score += 30
    elif structure_score < -10:
        confidence_score += 20
    else:
        penalties += 20  # Structure faible = grosse pénalité
    
    # Vérification direction structure vs IA
    if structure_bias in ["STRONG BULLISH", "BULLISH"] and pred_ia != 1:
        penalties += 25
    if structure_bias in ["STRONG BEARISH", "BEARISH"] and pred_ia != 0:
        penalties += 25
    
    # B. Bias HTF
    if score_htf > 7 and pred_ia == 1 and momentum_dir == "BUY":
        confidence_score += 25
    elif score_htf < -7 and pred_ia == 0 and momentum_dir == "SELL":
        confidence_score += 25
    elif score_htf > 4 and pred_ia == 1:
        confidence_score += 15
    elif score_htf < -4 and pred_ia == 0:
        confidence_score += 15
    else:
        penalties += 20
    
    # C. SMC
    if smc_score > 8 and pred_ia == 1:
        confidence_score += 20
    elif smc_score < -8 and pred_ia == 0:
        confidence_score += 20
    
    # D. Macro
    if macro_score > 12 and pred_ia == 1:
        confidence_score += 15
    elif macro_score < -12 and pred_ia == 0:
        confidence_score += 15
    else:
        penalties += 5
    
    # E. Régime
    if "TREND" in regime_nom:
        confidence_score += 15
    elif "RANGE" in regime_nom:
        penalties += 15
    elif "EXPLOSION" in regime_nom:
        penalties += 50
    
    # F. Momentum
    if momentum_score >= 45:
        confidence_score += 20
    elif momentum_score >= 35:
        confidence_score += 12
    
    # G. EMA
    close = df['Close'].iloc[-1]
    ema_50 = df['EMA_50'].iloc[-1]
    ema_200 = df['EMA_200'].iloc[-1]
    
    if ema_50 > ema_200 and close > ema_50 and pred_ia == 1:
        confidence_score += 12
    elif ema_50 < ema_200 and close < ema_50 and pred_ia == 0:
        confidence_score += 12
    else:
        penalties += 8
    
    # Score final
    confidence_score = max(0, confidence_score - penalties)
    confidence_score = min(99.9, confidence_score)

    # =========================================================
    # 🎯 DÉCISION FINALE SNIPER (SEUILS ULTRA ÉLEVÉS)
    # =========================================================
    signal = "NEUTRE"
    direction_trade = None

    # 🆕 SEUILS SNIPER
    if confidence_score >= 90:  # Premium ultra (au lieu de 85)
        signal = "🟢 STRONG BUY" if pred_ia == 1 else "🔴 STRONG SELL"
        direction_trade = "BUY" if pred_ia == 1 else "SELL"
    elif confidence_score >= 80:  # Good (au lieu de 70)
        signal = "🟢 MODERATE BUY" if pred_ia == 1 else "🔴 MODERATE SELL"
        direction_trade = "BUY" if pred_ia == 1 else "SELL"
    else:
        signal = "🟡 WAIT (Score insuffisant)"

    # Vérification finale
    if direction_trade and direction_trade != momentum_dir:
        signal = "🟡 WAIT (Divergence Momentum)"
        direction_trade = None
        confidence_score = 0

    # Calcul SL/TP
    sl, tp = 0, 0
    risk_msg = "N/A"
    
    if direction_trade:
        sl, tp, risk_dist, risk_msg = calculate_dynamic_risk(df, direction_trade, atr)
        if sl is None:
            signal = "🟡 WAIT (R:R Invalid)"
            confidence_score = 0
        else:
            # R:R minimum 2.8:1 (au lieu de 2.5)
            rr_ratio = abs(tp - close) / abs(close - sl)
            if rr_ratio < 2.8:
                signal = "🟡 WAIT (R:R < 2.8:1)"
                confidence_score = 0
                direction_trade = None
            else:
                # Log si score >= 85 (au lieu de 75)
                if confidence_score >= 85:
                    log_trade(direction_trade, close, confidence_score, 
                             f"SNIPER: {structure_bias} | {fib_zone} | {bos_type}", sl, tp)

    # Log complet
    full_log = {
        "htf": f"{'Bullish' if score_htf > 0 else 'Bearish'} ({score_htf})",
        "dxy": f"{'Bearish' if macro_score > 0 else 'Bullish'} ({macro_score})",
        "smc": smc_raison,
        "momentum": f"{momentum_dir} ({momentum_score}/50)",
        "structure": f"{structure_bias} (Score: {structure_score})",
        "fib_zone": fib_zone,
        "bos": bos_type,
        "order_block": structure_log['order_block'],
        "fvg": structure_log['fvg'],
        "mss": structure_log['mss'],
        "risk": risk_msg,
        "regime": regime_nom,
        "session": session_msg,
        "volume_quality": volume_msg
    }

    return df, signal, confidence_score, sl, tp, atr, model.feature_importances_, full_log, smc_score