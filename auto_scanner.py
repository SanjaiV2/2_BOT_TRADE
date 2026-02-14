import time
import json
import os
from ai_brain import get_ai_prediction
import requests

TELEGRAM_TOKEN = "8149629372:AAGnAdf0QLNOHSBHNC5HYmvWuyoEqWJqEIo"
ADMIN_ID = "5220624399"
DB_FILE = "subscribers.json"

def diffuser(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_ID, "text": message, "parse_mode": "Markdown"})
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                for sub in json.load(f):
                    requests.post(url, data={"chat_id": sub, "text": message, "parse_mode": "Markdown"})
    except: pass

print("🦅 PREDATOR V12 INSTITUTIONAL - Active.")
last_sig = None

while True:
    try:
        # Récupération complète
        df, sig, score, sl, tp, atr, imp, log_data, smc = get_ai_prediction(interval="15m")
        
        if df is not None:
            # FILTRE DE QUALITÉ (Point 1)
            # On envoie seulement si Score > 60 (Moderate) ou > 80 (Strong)
            if score >= 60.0:
                if sig != last_sig:
                    p = df['Close'].iloc[-1]
                    
                    # 9️⃣ SIGNAL QUALITY TAG (Format Pro)
                    icon = "💎" if score >= 80 else "🔔"
                    rr_ratio = abs(tp - p) / abs(p - sl) if sl != 0 else 0
                    
                    msg = (f"{icon} *PREDATOR SIGNAL V12*\n\n"
                           f"{sig}\n"
                           f"📊 *Confidence*: {score:.1f}%\n"
                           f"💵 *Price*: {p:.2f}\n\n"
                           f"🏗️ *HTF Bias*: {log_data['htf']}\n"
                           f"💲 *DXY*: {log_data['dxy']}\n"
                           f"🪤 *Liquidity*: {log_data['smc']}\n"
                           f"🛡️ *Risk Check*: {log_data['risk']}\n\n"
                           f"⚖️ *R:R Ratio*: 1:{rr_ratio:.2f}\n"
                           f"✅ *TP*: {tp:.2f}\n"
                           f"⛔ *SL*: {sl:.2f}")
                    
                    diffuser(msg)
                    last_sig = sig
                    print(f"✅ Signal envoyé : {sig} ({score:.1f}%)")
            else:
                # Feedback console pour toi (pour savoir pourquoi il attend)
                if "WAIT" not in sig:
                    print(f"💤 Score faible ({score:.1f}%). Filtre: {log_data.get('risk', 'Score')}")
                else:
                    print(f"💤 {sig}")
        
        else:
            print(f"💤 {sig}") # Marché fermé

    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    time.sleep(60)