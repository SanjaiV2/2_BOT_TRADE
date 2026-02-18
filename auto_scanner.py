import time
import json
import os
from datetime import datetime, timedelta
import pytz
from ai_brain import get_ai_prediction
import requests

TELEGRAM_TOKEN = "8149629372:AAGnAdf0QLNOHSBHNC5HYmvWuyoEqWJqEIo"
ADMIN_ID = "5220624399"
DB_FILE = "subscribers.json"

# =========================================================
# ⚙️ CONFIG SCANNER - STYLE: SWING 1H / SORTIE 30min-2h
# =========================================================
INTERVAL          = "1h"     # Timeframe principal
SCAN_EVERY        = 300      # Scan toutes les 5 min (inutile de scanner chaque minute sur 1h)
MIN_SCORE_SIGNAL  = 70.0     # Score minimum pour envoyer
MIN_SCORE_STRONG  = 85.0     # Score pour signal STRONG (💎)
MAX_SIGNALS_DAY   = 2        # Maximum 2 signaux par jour
COOLDOWN_SIGNAL   = 90       # Minimum 90 min entre 2 signaux

# =========================================================
# 📊 ÉTAT INTERNE
# =========================================================
last_sig         = None
last_signal_time = None
signals_today    = 0
last_reset_day   = datetime.now(pytz.utc).date()

def diffuser(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_ID, "text": message, "parse_mode": "Markdown"})
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                for sub in json.load(f):
                    requests.post(url, data={"chat_id": sub, "text": message, "parse_mode": "Markdown"})
    except: pass

def reset_daily_counter():
    global signals_today, last_reset_day
    today = datetime.now(pytz.utc).date()
    if today != last_reset_day:
        signals_today = 0
        last_reset_day = today
        print(f"🔄 Nouveau jour — Compteur remis à zéro")

def can_send_signal():
    global last_signal_time, signals_today
    if signals_today >= MAX_SIGNALS_DAY:
        return False, f"Limite journalière atteinte ({MAX_SIGNALS_DAY}/jour)"
    if last_signal_time:
        elapsed = (datetime.now(pytz.utc) - last_signal_time).seconds / 60
        if elapsed < COOLDOWN_SIGNAL:
            remaining = int(COOLDOWN_SIGNAL - elapsed)
            return False, f"Cooldown actif ({remaining} min restantes)"
    return True, "OK"

def build_message(sig, score, p, sl, tp, log_data, rr_ratio, paris_time):
    icon    = "💎" if score >= MIN_SCORE_STRONG else "🔔"
    qualite = "SIGNAL PREMIUM" if score >= MIN_SCORE_STRONG else "SIGNAL VALIDE"
    fleche  = "📈" if "BUY" in sig else "📉"

    htf      = log_data.get('htf', 'N/A')
    dxy      = log_data.get('dxy', 'N/A')
    smc      = log_data.get('smc', 'N/A')
    risk     = log_data.get('risk', 'N/A')
    regime   = log_data.get('regime', 'N/A')
    session  = log_data.get('session', 'N/A')
    momentum = log_data.get('momentum', 'N/A')

    return (
        f"{icon} *PREDATOR X — {qualite}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{fleche} *Direction* : `{sig}`\n"
        f"📊 *Confiance* : `{score:.1f}%`\n"
        f"💵 *Prix* : `{p:.2f} $`\n"
        f"⏱ *Timeframe* : `1H`\n"
        f"🕐 *Durée estimée* : `30min — 2h`\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ *Take Profit* : `{tp:.2f} $`\n"
        f"⛔ *Stop Loss* : `{sl:.2f} $`\n"
        f"⚖️ *Risk/Reward* : `1:{rr_ratio:.2f}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🏗️ *HTF Bias* : `{htf}`\n"
        f"💲 *DXY* : `{dxy}`\n"
        f"🪤 *SMC* : `{smc}`\n"
        f"📈 *Momentum* : `{momentum}`\n"
        f"🌊 *Régime* : `{regime}`\n"
        f"🛡️ *Risk* : `{risk}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🕐 `{paris_time} Paris` | Session: `{session}`\n"
        f"_⚠️ Toujours vérifier avant d'entrer._"
    )

# =========================================================
# 🚀 BOUCLE PRINCIPALE
# =========================================================
print("🦅 PREDATOR V12 — Scanner SWING 1H actif.")
print(f"⚙️  Config: {MAX_SIGNALS_DAY} signaux max/jour | Score min: {MIN_SCORE_SIGNAL}% | Cooldown: {COOLDOWN_SIGNAL}min")
print(f"⏱  Scan toutes les {SCAN_EVERY//60} minutes\n")

while True:
    try:
        reset_daily_counter()

        now_paris  = datetime.now(pytz.timezone("Europe/Paris"))
        paris_time = now_paris.strftime("%H:%M")

        df, sig, score, sl, tp, atr, imp, log_data, smc_score = get_ai_prediction(interval=INTERVAL)

        if df is None:
            print(f"[{paris_time}] 💤 {sig}")

        else:
            print(f"[{paris_time}] 📡 {sig} | Score: {score:.1f}%")

            if score >= MIN_SCORE_SIGNAL:
                can_send, reason = can_send_signal()

                if not can_send:
                    print(f"[{paris_time}] ⏸  Bloqué — {reason}")

                elif sig == last_sig and score < MIN_SCORE_STRONG:
                    print(f"[{paris_time}] 🔁 Même signal, on attend un changement")

                else:
                    p        = df['Close'].iloc[-1]
                    rr_ratio = abs(tp - p) / abs(p - sl) if sl != 0 else 0
                    message  = build_message(sig, score, p, sl, tp, log_data, rr_ratio, paris_time)

                    diffuser(message)

                    last_sig         = sig
                    last_signal_time = datetime.now(pytz.utc)
                    signals_today   += 1

                    print(f"[{paris_time}] ✅ Signal envoyé ! ({signals_today}/{MAX_SIGNALS_DAY} aujourd'hui)")
            else:
                if score > 0:
                    print(f"[{paris_time}] 💤 Score trop faible : {score:.1f}%")

    except Exception as e:
        print(f"❌ Erreur: {e}")

    time.sleep(SCAN_EVERY)