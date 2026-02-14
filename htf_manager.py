import yfinance as yf
import pandas as pd
import numpy as np

def get_market_structure(df):
    """
    Détermine la structure : HH/HL (Haussier) ou LH/LL (Baissier)
    """
    if df.empty: return "NEUTRE"
    
    # On utilise les prix de clôture pour éviter le bruit des mèches
    current_close = df['Close'].iloc[-1]
    
    # On regarde les 10 dernières bougies pour trouver le "Range" récent
    recent_high = df['High'].iloc[-10:-1].max()
    recent_low = df['Low'].iloc[-10:-1].min()
    
    # Moyenne Mobile 50 pour la tendance de fond simple
    ma_50 = df['Close'].rolling(50).mean().iloc[-1]
    
    structure = "NEUTRE"
    
    # Logique de Structure
    if current_close > recent_high:
        structure = "BULLISH BREAK (HH)"
    elif current_close < recent_low:
        structure = "BEARISH BREAK (LL)"
    else:
        # Si on est dans le range, on utilise la MA50
        if current_close > ma_50: structure = "BULLISH TREND"
        else: structure = "BEARISH TREND"

    return structure

def analyze_htf_bias(current_interval):
    """
    Choisit intelligemment les Timeframes Supérieurs à analyser
    en fonction de ce que tu trades.
    """
    # 1. SÉLECTION DYNAMIQUE DES TIMEFRAMES SUPÉRIEURS (HTF)
    # yfinance ne gère pas le 4h nativement de façon fiable, on utilise 1h, 1d, 1wk, 1mo
    
    htf_1 = "1h"
    htf_2 = "1d"
    
    if current_interval in ["1m", "2m", "5m", "15m", "30m"]:
        htf_1 = "1h"  # Tendance Intraday
        htf_2 = "1d"  # Tendance de Fond
        
    elif current_interval == "1h":
        htf_1 = "1d"  # Tendance Journalière
        htf_2 = "1wk" # Tendance Hebdomadaire (Gros Swing)
        
    elif current_interval == "1d":
        htf_1 = "1wk"
        htf_2 = "1mo"
        
    # Cas par défaut ou exotique
    else:
        htf_1 = "1d"
        htf_2 = "1wk"

    try:
        # 2. TÉLÉCHARGEMENT DES DONNÉES ADAPTÉES
        # On prend assez d'historique pour calculer la MA50
        # interval=htf_1
        data_1 = yf.Ticker("GC=F").history(period="6mo", interval=htf_1)
        data_2 = yf.Ticker("GC=F").history(period="2y", interval=htf_2)
        
        if data_1.empty or data_2.empty: return "N/A", "N/A", 0

        # 3. ANALYSE STRUCTURELLE
        bias_1 = get_market_structure(data_1)
        bias_2 = get_market_structure(data_2)
        
        # 4. CALCUL DU SCORE CONFLUENCE (-10 à +10)
        score_bias = 0
        
        # Le HTF le plus grand (2) pèse plus lourd
        if "BULLISH" in bias_2: score_bias += 6
        elif "BEARISH" in bias_2: score_bias -= 6
        
        # Le HTF intermédiaire (1) affine
        if "BULLISH" in bias_1: score_bias += 4
        elif "BEARISH" in bias_1: score_bias -= 4
        
        # Résultat : 
        # +10 = Les deux HTF sont Haussiers (Achat Blindé)
        # -10 = Les deux HTF sont Baissiers (Vente Blindée)
        # 0 ou +/- 2 = Conflit (Range probable)
        
        return bias_1, bias_2, score_bias, htf_1, htf_2

    except Exception as e:
        return "Erreur", str(e), 0, htf_1, htf_2