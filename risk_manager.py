import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

JOURNAL_FILE = "trading_journal.json"

# Initialisation du journal si absent
if not os.path.exists(JOURNAL_FILE):
    with open(JOURNAL_FILE, "w") as f: json.dump([], f)

def get_journal():
    with open(JOURNAL_FILE, "r") as f: return json.load(f)

def save_journal(entry):
    data = get_journal()
    data.append(entry)
    with open(JOURNAL_FILE, "w") as f: json.dump(data, f)

def check_volatility_kill_switch(df):
    """
    3️⃣ Volatility Kill Switch : Si l'ATR explose, on coupe tout.
    """
    atr = df['ATR'].iloc[-1]
    atr_mean = df['ATR'].rolling(50).mean().iloc[-1]
    
    # Si la volatilité actuelle est 2x supérieure à la moyenne = DANGER (News, Crash)
    if atr > (atr_mean * 2.0):
        return True, f"⚠️ KILL SWITCH ACTIVÉ : Volatilité extrême ({atr:.2f})"
    return False, "Volatilité Normale"

def check_cooldown():
    """
    4️⃣ Trade Cooldown : Vérifie si on a le droit de trader après pertes/gains.
    """
    data = get_journal()
    if not data: return True, "Prêt"

    last_trades = data[-3:] # Les 3 derniers trades
    now = datetime.now()
    
    # Récupérer le dernier trade
    try:
        last_time = datetime.fromisoformat(last_trades[-1]['timestamp'])
    except:
        return True, "Prêt"

    # Règle : Pause 1h après une perte (Simulation ici, à adapter avec PnL réel)
    # Dans une vraie version, tu connecterais l'API broker pour voir le PnL.
    # Ici on met une pause simple de 15 min entre chaque trade pour éviter l'overtrading.
    if (now - last_time) < timedelta(minutes=15):
        return False, "⏳ COOLDOWN : Pause entre trades"

    return True, "Prêt"

def calculate_dynamic_risk(df, direction, atr):
    """
    2️⃣ Dynamic Risk Engine : SL sur structure, TP sur volatilité.
    """
    close = df['Close'].iloc[-1]
    
    # Trouver le dernier Swing Low / High (Structure réelle) sur 5 bougies
    last_low = df['Low'].iloc[-10:-1].min()
    last_high = df['High'].iloc[-10:-1].max()

    sl = 0
    tp = 0
    
    if direction == "BUY":
        # SL sous le dernier creux structurel (ou min 1.5 ATR)
        structure_sl = last_low
        min_atr_sl = close - (atr * 1.5)
        sl = min(structure_sl, min_atr_sl) # On prend le plus bas pour être safe
        
        risk = close - sl
        tp = close + (risk * 2.5) # R:R de 1:2.5
        
    elif direction == "SELL":
        # SL au-dessus du dernier sommet structurel
        structure_sl = last_high
        min_atr_sl = close + (atr * 1.5)
        sl = max(structure_sl, min_atr_sl)
        
        risk = sl - close
        tp = close - (risk * 2.5)

    # Vérification Ratio R:R (Pas de trade si < 1.8)
    # Ici c'est forcé à 2.5 par le calcul, mais on pourrait vérifier la distance
    risk_pips = abs(close - sl)
    if risk_pips < 0.5: # Si le SL est trop collé (bruit)
        return None, None, 0, "❌ SL trop serré (Bruit)"

    return sl, tp, risk_pips, "✅ R:R Validé"

def log_trade(action, price, score, reason, sl, tp):
    """
    1️⃣0️⃣ Journal interne
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "price": price,
        "score": score,
        "sl": sl,
        "tp": tp,
        "reason": reason
    }
    save_journal(entry)