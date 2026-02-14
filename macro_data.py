import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator

def analyze_macro_context(interval="1h"):
    """
    Analyse le contexte Macro-Économique (Yields US + Silver).
    Retourne : (Score Impact, Explication)
    """
    try:
        # On récupère les Taux US 10 ans (^TNX) et l'Argent (SI=F)
        # On utilise le timeframe 1h pour la macro, c'est plus stable
        tickers = yf.download("^TNX SI=F", period="5d", interval="1h", progress=False)
        
        # Gestion des multi-index de yfinance
        if 'Close' in tickers.columns:
            us10y = tickers['Close']['^TNX']
            silver = tickers['Close']['SI=F']
        else:
            return 0, "Données Macro Indisponibles"

    except Exception as e:
        return 0, f"Erreur Macro: {str(e)}"

    score_macro = 0
    raison = []

    # 1. ANALYSE DES TAUX US (US10Y) - L'ennemi de l'Or
    # Si les taux sont au-dessus de leur moyenne (EMA 50), c'est baissier pour l'Or
    ema_rates = EMAIndicator(us10y, window=50).ema_indicator().iloc[-1]
    current_rate = us10y.iloc[-1]
    
    if current_rate > ema_rates:
        score_macro -= 15 # Pénalité forte
        raison.append("⚠️ Taux US 10Y Haussiers (Pression Vendeuse)")
    else:
        score_macro += 5 # Soutien léger
        raison.append("✅ Taux US Calmes")

    # 2. ANALYSE DU SILVER (Le confirrmateur)
    # On regarde juste la tendance court terme du Silver
    silver_change = silver.pct_change().iloc[-1]
    
    if silver_change > 0.001: # Si l'Argent monte > 0.1%
        score_macro += 10
        raison.append("✅ Silver Confirme la Hausse")
    elif silver_change < -0.001: # Si l'Argent baisse
        score_macro -= 10
        raison.append("⚠️ Silver Diverge (Baisse)")

    # Synthèse textuelle
    explication = " / ".join(raison)
    return score_macro, explication