import time
import json
import os
from datetime import datetime
import pytz
from ai_brain import get_ai_prediction  # Version SNIPER
from mt5_connector import MT5Connector
from position_manager import PositionManager
import requests

# =========================================================
# ⚙️ CONFIGURATION
# =========================================================

# Telegram
TELEGRAM_TOKEN = "8149629372:AAGnAdf0QLNOHSBHNC5HYmvWuyoEqWJqEIo"
ADMIN_ID = "5220624399"

# MT5 (À CONFIGURER)
MT5_LOGIN = 103265983
MT5_PASSWORD = "-q1rAdRl"
MT5_SERVER = "MetaQuotes-Demo"  # TON SERVEUR (ex: "MetaQuotes-Demo")

# Trading
INTERVAL = "1h"
SCAN_EVERY = 300  # 5 minutes
MIN_SCORE_SIGNAL = 80.0  # Score minimum (SNIPER)

# =========================================================
# 📱 TELEGRAM
# =========================================================

def send_telegram(message):
    """Envoie notification Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
    except:
        pass

# =========================================================
# 🤖 TRADER AUTOMATIQUE
# =========================================================

def build_telegram_alert(action, price, sl, tp, score, signal_info, lot_size):
    """Construit message Telegram détaillé"""
    emoji = "🟢" if action == "BUY" else "🔴"
    rr = abs(tp - price) / abs(price - sl) if sl != 0 else 0
    
    return (
        f"{emoji} *TRADE AUTOMATIQUE EXÉCUTÉ*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 *Direction*: `{action}`\n"
        f"💰 *Prix*: `{price:.2f} $`\n"
        f"📊 *Lot*: `{lot_size}`\n"
        f"🎯 *Score*: `{score:.1f}%`\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ *TP*: `{tp:.2f} $`\n"
        f"⛔ *SL*: `{sl:.2f} $`\n"
        f"⚖️ *R:R*: `1:{rr:.2f}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🧠 *Setup*:\n"
        f"`{signal_info}`\n\n"
        f"⏰ `{datetime.now(pytz.timezone('Europe/Paris')).strftime('%H:%M')}`"
    )

def main():
    """Boucle principale du trader automatique"""
    
    print("=" * 60)
    print("🤖 PREDATOR X - TRADER AUTOMATIQUE SNIPER")
    print("=" * 60)
    
    # Connexion MT5
    print("\n🔌 Connexion à MetaTrader 5...")
    mt5 = MT5Connector(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
    
    if not mt5.connect():
        print("❌ ERREUR: Impossible de se connecter à MT5")
        print("Vérifiez vos identifiants dans le fichier auto_trader.py")
        send_telegram("❌ *ERREUR CRITIQUE*\nImpossible de se connecter à MT5")
        return
    
    # Initialisation Position Manager
    print("📊 Initialisation du gestionnaire de positions...")
    pm = PositionManager(mt5)
    
    print("\n✅ Système opérationnel !")
    print(f"⚙️  Config:")
    print(f"   - Timeframe: {INTERVAL}")
    print(f"   - Scan: toutes les {SCAN_EVERY//60} min")
    print(f"   - Score min: {MIN_SCORE_SIGNAL}%")
    print(f"   - Max positions: {pm.config['max_positions']}")
    print(f"   - Max trades/jour: {pm.config['max_daily_trades']}")
    print(f"   - Risk/trade: {pm.config['risk_per_trade']}%")
    print(f"   - Trailing stop: {'✅' if pm.config['trailing_stop_enabled'] else '❌'}")
    print(f"   - Break even: {'✅' if pm.config['break_even_enabled'] else '❌'}\n")
    
    send_telegram(
        "🤖 *PREDATOR TRADER AUTOMATIQUE*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ Système démarré\n"
        "📡 Scanner actif\n"
        "🎯 Mode: SNIPER\n\n"
        f"⚙️ Max: {pm.config['max_daily_trades']} trades/jour\n"
        f"💰 Risk: {pm.config['risk_per_trade']}% par trade"
    )
    
    # Variables d'état
    last_signal = None
    scan_count = 0
    
    # Boucle principale
    while True:
        try:
            scan_count += 1
            now_paris = datetime.now(pytz.timezone("Europe/Paris"))
            paris_time = now_paris.strftime("%H:%M")
            
            # Gestion des positions ouvertes
            pm.manage_open_positions()
            pm.update_daily_profit()
            
            # Récupération du signal
            df, sig, score, sl, tp, atr, imp, log_data, smc_score = get_ai_prediction(interval=INTERVAL)
            
            # Affichage status
            if scan_count % 6 == 0:  # Toutes les 30 min
                stats = pm.get_statistics()
                print(f"\n[{paris_time}] 📊 Status:")
                print(f"   Balance: {stats['balance']:.2f} | Equity: {stats['equity']:.2f}")
                print(f"   Trades today: {stats['daily_trades']}/{stats['max_daily_trades']}")
                print(f"   P&L jour: {stats['daily_profit']:.2f}")
                print(f"   Positions: {stats['open_positions']}")
            
            # Si marché fermé ou session inactive
            if df is None:
                print(f"[{paris_time}] 💤 {sig}")
                time.sleep(SCAN_EVERY)
                continue
            
            # Affichage scan
            print(f"[{paris_time}] 📡 {sig} | Score: {score:.1f}%")
            
            # Vérifier si signal tradable
            if score >= MIN_SCORE_SIGNAL and "WAIT" not in sig and "NEUTRE" not in sig:
                
                # Vérifier si on peut ouvrir position
                can_open, reason = pm.can_open_position()
                
                if not can_open:
                    print(f"[{paris_time}] ⏸️  Signal ignoré: {reason}")
                
                # Éviter signal identique
                elif sig == last_signal:
                    print(f"[{paris_time}] 🔁 Signal identique, on attend changement")
                
                else:
                    # 🚀 OUVERTURE POSITION AUTOMATIQUE
                    direction = "BUY" if "BUY" in sig else "SELL"
                    
                    # Info détaillée pour log
                    signal_info = (
                        f"{log_data.get('structure', 'N/A')} | "
                        f"{log_data.get('fib_zone', 'N/A')} | "
                        f"{log_data.get('bos', 'N/A')}"
                    )
                    
                    # Ouverture
                    result = pm.open_position(
                        direction=direction,
                        sl_price=sl,
                        tp_price=tp,
                        signal_info=signal_info
                    )
                    
                    if result:
                        last_signal = sig
                        
                        # Notification Telegram
                        price = df['Close'].iloc[-1]
                        lot = pm.mt5.calculate_lot_size(
                            risk_percent=pm.config['risk_per_trade'],
                            sl_distance=abs(price - sl)
                        )
                        
                        msg = build_telegram_alert(
                            direction, price, sl, tp, score, signal_info, lot
                        )
                        send_telegram(msg)
                        
                        print(f"[{paris_time}] ✅ TRADE EXÉCUTÉ !")
                    else:
                        print(f"[{paris_time}] ❌ Échec ouverture position")
            
            else:
                if score > 0 and score < MIN_SCORE_SIGNAL:
                    print(f"[{paris_time}] 💤 Score insuffisant: {score:.1f}%")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt demandé par l'utilisateur")
            break
            
        except Exception as e:
            print(f"\n❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()
            send_telegram(f"⚠️ *ERREUR TRADER*\n```{str(e)[:200]}```")
        
        time.sleep(SCAN_EVERY)
    
    # Arrêt propre
    print("\n🔌 Déconnexion MT5...")
    mt5.disconnect()
    send_telegram("🛑 *TRADER ARRÊTÉ*\nDéconnexion MT5")
    print("✅ Arrêt complet\n")

if __name__ == "__main__":
    main()