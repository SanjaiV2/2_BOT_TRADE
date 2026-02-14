import pandas as pd
import numpy as np
from ta.trend import ADXIndicator
from ta.volatility import AverageTrueRange, BollingerBands

def detect_market_regime(df):
    """
    Analyse le régime de marché : TREND, RANGE, ou VOLATILE.
    Retourne : (String regime, Score force 0-100)
    """
    # 1. Calculs intermédiaires
    adx = ADXIndicator(df['High'], df['Low'], df['Close'], window=14).adx().iloc[-1]
    
    bb = BollingerBands(df['Close'], window=20, window_dev=2)
    bb_width = (bb.bollinger_hband().iloc[-1] - bb.bollinger_lband().iloc[-1]) / bb.bollinger_mavg().iloc[-1]
    
    atr = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
    atr_current = atr.iloc[-1]
    atr_mean = atr.rolling(30).mean().iloc[-1] # Moyenne ATR sur 30 périodes
    
    regime = "NEUTRE"
    score_regime = 50

    # 2. Logique de classification
    
    # A. DÉTECTION DE TENDANCE (TREND)
    if adx > 25:
        regime = "TREND (Tendance)"
        score_regime = 80 + (adx - 25) # Plus l'ADX est haut, plus le score monte
        
    # B. DÉTECTION DE RANGE (COMPRESSION)
    # Si les bandes de Bollinger sont serrées et l'ADX faible
    elif bb_width < 0.0020 and adx < 20: 
        regime = "RANGE (Accumulation)"
        score_regime = 40 # En range, on réduit la confiance des signaux directionnels
        
    # C. DÉTECTION D'EXPLOSION (VOLATILITÉ / NEWS)
    # Si la volatilité actuelle est 50% supérieure à la moyenne
    elif atr_current > (atr_mean * 1.5):
        regime = "EXPLOSION (Haute Volatilité)"
        score_regime = 60 # Risqué mais profitable

    return regime, min(score_regime, 100), bb_width, atr_current