import pandas as pd
import numpy as np

def detect_false_breakout(df):
    """
    Détecte les Faux Breakouts, Liquidity Sweeps et Rejets Volumiques.
    Retourne : Score SMC (-10 à +10) et Raison
    """
    # Données actuelles
    open_p = df['Open'].iloc[-1]
    high_p = df['High'].iloc[-1]
    low_p = df['Low'].iloc[-1]
    close_p = df['Close'].iloc[-1]
    vol_p = df['Volume'].iloc[-1]
    
    # Moyennes
    avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
    prev_high = df['High'].iloc[-2]
    prev_low = df['Low'].iloc[-2]
    
    score_smc = 0
    raison = "Neutre"

    # 1. ANALYSE VOLUME SPIKE (L'effort)
    is_volume_spike = vol_p > (avg_vol * 1.5) # +50% de volume que d'habitude
    
    # 2. ANALYSE DES MÈCHES (Le rejet)
    body_size = abs(close_p - open_p)
    upper_wick = high_p - max(close_p, open_p)
    lower_wick = min(close_p, open_p) - low_p
    
    # 3. DÉTECTION "FALSE BREAKOUT" BEARISH (Bull Trap)
    # Le prix casse le haut précédent, mais clôture en bas avec une grosse mèche haute
    if high_p > prev_high and close_p < prev_high:
        if upper_wick > body_size * 2: # La mèche est 2x plus grande que le corps
            score_smc -= 10
            raison = "🔴 FALSE BREAKOUT (Bull Trap) + Rejet"
            if is_volume_spike: 
                score_smc -= 5
                raison += " + Vol Spike (Absorption)"

    # 4. DÉTECTION "FALSE BREAKOUT" BULLISH (Bear Trap / Stop Hunt)
    # Le prix casse le bas précédent, mais remonte violemment
    elif low_p < prev_low and close_p > prev_low:
        if lower_wick > body_size * 2:
            score_smc += 10
            raison = "🟢 LIQUIDITY SWEEP (Bear Trap)"
            if is_volume_spike:
                score_smc += 5
                raison += " + Vol Spike (Capitulation)"
    
    return score_smc, raison