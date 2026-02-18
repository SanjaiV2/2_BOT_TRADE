import pandas as pd
import numpy as np

def calculate_fibonacci_zones(df, lookback=50):
    """
    Calcule les zones Premium/Discount basées sur Fibonacci HTF
    Retourne : zone actuelle, score (-10 à +10)
    """
    # Swing High/Low sur la période
    swing_high = df['High'].rolling(lookback).max().iloc[-1]
    swing_low = df['Low'].rolling(lookback).min().iloc[-1]
    current_price = df['Close'].iloc[-1]
    
    # Range et niveaux Fibonacci
    range_size = swing_high - swing_low
    
    # Zones institutionnelles
    fib_0 = swing_low  # 0%
    fib_236 = swing_low + (range_size * 0.236)  # Discount extrême
    fib_382 = swing_low + (range_size * 0.382)  # Discount
    fib_50 = swing_low + (range_size * 0.50)   # Equilibrium (à éviter)
    fib_618 = swing_low + (range_size * 0.618)  # Premium
    fib_764 = swing_low + (range_size * 0.764)  # Premium extrême
    fib_100 = swing_high  # 100%
    
    zone = "EQUILIBRIUM"
    score = 0
    
    # Classification de la zone
    if current_price <= fib_382:
        zone = "DISCOUNT PREMIUM"  # Zone d'achat institutionnelle
        score = 10  # Bullish bias fort
    elif fib_382 < current_price <= fib_50:
        zone = "DISCOUNT"
        score = 5
    elif fib_50 < current_price < fib_618:
        zone = "EQUILIBRIUM"  # ⚠️ ZONE À ÉVITER
        score = -5  # Pénalité
    elif fib_618 <= current_price < fib_764:
        zone = "PREMIUM"
        score = -5  # Bearish bias
    else:  # >= fib_764
        zone = "PREMIUM EXTREME"  # Zone de vente institutionnelle
        score = -10  # Bearish bias fort
    
    return zone, score, {
        'swing_high': swing_high,
        'swing_low': swing_low,
        'fib_levels': {
            '0.00': fib_0,
            '0.236': fib_236,
            '0.382': fib_382,
            '0.500': fib_50,
            '0.618': fib_618,
            '0.764': fib_764,
            '1.00': fib_100
        }
    }

def detect_break_of_structure(df, lookback=20):
    """
    Détecte un Break of Structure (BOS) - cassure de structure haussière/baissière
    Un BOS valide = prix casse un swing high/low significatif avec volume
    """
    # Identifier les swing highs et lows
    highs = df['High'].rolling(window=5, center=True).max()
    lows = df['Low'].rolling(window=5, center=True).min()
    
    # Swing points (où le prix = extremum local)
    df['swing_high'] = df['High'] == highs
    df['swing_low'] = df['Low'] == lows
    
    # Dernier swing high et low significatifs
    recent_swing_high = df[df['swing_high']]['High'].tail(3).max() if any(df['swing_high']) else df['High'].max()
    recent_swing_low = df[df['swing_low']]['Low'].tail(3).min() if any(df['swing_low']) else df['Low'].min()
    
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume'].rolling(20).mean().iloc[-1]
    
    bos_detected = False
    bos_type = "NONE"
    bos_score = 0
    
    # BOS BULLISH : Prix casse au-dessus du dernier swing high avec volume
    if current_price > recent_swing_high and prev_price <= recent_swing_high:
        if current_volume > avg_volume * 1.2:  # Volume confirmation
            bos_detected = True
            bos_type = "BULLISH BOS"
            bos_score = 15
        else:
            bos_type = "WEAK BULLISH BOS"
            bos_score = 5
    
    # BOS BEARISH : Prix casse en-dessous du dernier swing low avec volume
    elif current_price < recent_swing_low and prev_price >= recent_swing_low:
        if current_volume > avg_volume * 1.2:
            bos_detected = True
            bos_type = "BEARISH BOS"
            bos_score = -15
        else:
            bos_type = "WEAK BEARISH BOS"
            bos_score = -5
    
    return bos_detected, bos_type, bos_score, recent_swing_high, recent_swing_low

def detect_order_blocks(df, lookback=30):
    """
    Détecte les Order Blocks - dernières bougies avant un mouvement fort
    OB = Zone où les institutions ont placé des ordres
    """
    order_blocks = []
    
    for i in range(len(df) - lookback, len(df) - 1):
        if i < 2:
            continue
            
        # Mouvement fort = bougie avec range > 1.5x ATR
        atr = (df['High'].iloc[i] - df['Low'].iloc[i])
        avg_range = (df['High'] - df['Low']).rolling(14).mean().iloc[i]
        
        is_strong_move = atr > (avg_range * 1.5)
        
        if is_strong_move:
            # Bullish OB = dernière bougie baissière avant mouvement haussier
            if df['Close'].iloc[i] > df['Open'].iloc[i]:  # Bougie haussière
                if df['Close'].iloc[i-1] < df['Open'].iloc[i-1]:  # Bougie précédente baissière
                    ob = {
                        'type': 'BULLISH',
                        'high': df['High'].iloc[i-1],
                        'low': df['Low'].iloc[i-1],
                        'index': i-1
                    }
                    order_blocks.append(ob)
            
            # Bearish OB = dernière bougie haussière avant mouvement baissier
            elif df['Close'].iloc[i] < df['Open'].iloc[i]:
                if df['Close'].iloc[i-1] > df['Open'].iloc[i-1]:
                    ob = {
                        'type': 'BEARISH',
                        'high': df['High'].iloc[i-1],
                        'low': df['Low'].iloc[i-1],
                        'index': i-1
                    }
                    order_blocks.append(ob)
    
    # Vérifier si le prix actuel est proche d'un OB
    current_price = df['Close'].iloc[-1]
    nearest_ob = None
    min_distance = float('inf')
    
    for ob in order_blocks[-5:]:  # Les 5 derniers OB
        distance = min(abs(current_price - ob['low']), abs(current_price - ob['high']))
        if distance < min_distance:
            min_distance = distance
            nearest_ob = ob
    
    if nearest_ob and min_distance < (df['ATR'].iloc[-1] * 0.5):  # Prix proche d'un OB (< 0.5 ATR)
        return True, nearest_ob['type'], 10 if nearest_ob['type'] == 'BULLISH' else -10
    
    return False, "NONE", 0

def detect_fair_value_gap(df):
    """
    Détecte les Fair Value Gaps (FVG) - zones de déséquilibre
    FVG = Gap entre le high de bougie N-2 et le low de bougie N (ou inverse)
    """
    if len(df) < 3:
        return False, "NONE", 0
    
    # Bullish FVG : Low de bougie actuelle > High de bougie il y a 2
    bullish_fvg = df['Low'].iloc[-1] > df['High'].iloc[-3]
    
    # Bearish FVG : High de bougie actuelle < Low de bougie il y a 2
    bearish_fvg = df['High'].iloc[-1] < df['Low'].iloc[-3]
    
    if bullish_fvg:
        gap_size = df['Low'].iloc[-1] - df['High'].iloc[-3]
        if gap_size > df['ATR'].iloc[-1] * 0.3:  # Gap significatif
            return True, "BULLISH FVG", 8
    
    if bearish_fvg:
        gap_size = df['Low'].iloc[-3] - df['High'].iloc[-1]
        if gap_size > df['ATR'].iloc[-1] * 0.3:
            return True, "BEARISH FVG", -8
    
    return False, "NONE", 0

def detect_market_structure_shift(df, lookback=15):
    """
    Détecte un Market Structure Shift (MSS) - changement de tendance
    MSS = Cassure de structure + création d'un nouveau swing opposé
    """
    # Structure actuelle basée sur les swings récents
    recent_highs = []
    recent_lows = []
    
    for i in range(len(df) - lookback, len(df)):
        if i < 2 or i >= len(df) - 1:
            continue
        
        # Swing high = prix plus haut que les 2 bougies de chaque côté
        if df['High'].iloc[i] > df['High'].iloc[i-1] and df['High'].iloc[i] > df['High'].iloc[i+1]:
            recent_highs.append((i, df['High'].iloc[i]))
        
        # Swing low
        if df['Low'].iloc[i] < df['Low'].iloc[i-1] and df['Low'].iloc[i] < df['Low'].iloc[i+1]:
            recent_lows.append((i, df['Low'].iloc[i]))
    
    if len(recent_highs) < 2 or len(recent_lows) < 2:
        return False, "NONE", 0
    
    # BULLISH MSS : Structure de Lower Lows → Higher Low créé
    if len(recent_lows) >= 2:
        last_low = recent_lows[-1][1]
        prev_low = recent_lows[-2][1]
        
        if last_low > prev_low:  # Higher Low créé
            # Vérifier si on a aussi cassé un high
            if len(recent_highs) >= 1 and df['Close'].iloc[-1] > recent_highs[-1][1]:
                return True, "BULLISH MSS", 20  # Fort signal
    
    # BEARISH MSS : Structure de Higher Highs → Lower High créé
    if len(recent_highs) >= 2:
        last_high = recent_highs[-1][1]
        prev_high = recent_highs[-2][1]
        
        if last_high < prev_high:  # Lower High créé
            if len(recent_lows) >= 1 and df['Close'].iloc[-1] < recent_lows[-1][1]:
                return True, "BEARISH MSS", -20
    
    return False, "NONE", 0

def analyze_institutional_structure(df):
    """
    Fonction principale - Analyse complète structure institutionnelle
    """
    # 1. Premium/Discount zones
    fib_zone, fib_score, fib_data = calculate_fibonacci_zones(df, lookback=100)
    
    # 2. Break of Structure
    bos_detected, bos_type, bos_score, swing_high, swing_low = detect_break_of_structure(df)
    
    # 3. Order Blocks
    ob_present, ob_type, ob_score = detect_order_blocks(df)
    
    # 4. Fair Value Gaps
    fvg_present, fvg_type, fvg_score = detect_fair_value_gap(df)
    
    # 5. Market Structure Shift
    mss_detected, mss_type, mss_score = detect_market_structure_shift(df)
    
    # SCORE TOTAL
    structure_score = fib_score + bos_score + ob_score + fvg_score + mss_score
    
    # Détermination bias structurel
    structure_bias = "NEUTRAL"
    if structure_score > 20:
        structure_bias = "STRONG BULLISH"
    elif structure_score > 10:
        structure_bias = "BULLISH"
    elif structure_score < -20:
        structure_bias = "STRONG BEARISH"
    elif structure_score < -10:
        structure_bias = "BEARISH"
    
    # Log détaillé
    structure_log = {
        'bias': structure_bias,
        'score': structure_score,
        'fib_zone': fib_zone,
        'bos': bos_type,
        'order_block': ob_type if ob_present else "NONE",
        'fvg': fvg_type,
        'mss': mss_type,
        'swing_high': swing_high,
        'swing_low': swing_low
    }
    
    return structure_score, structure_bias, structure_log