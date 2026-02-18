import MetaTrader5 as mt5
from datetime import datetime

SYMBOL = "XAUUSD"
LOT_SIZE = 0.1

def connect_mt5():
    if not mt5.initialize():
        print("❌ Erreur connexion MT5:", mt5.last_error())
        return False
    print("✅ Connecté à MT5")
    return True


def has_open_position():
    positions = mt5.positions_get(symbol=SYMBOL)
    if positions and len(positions) > 0:
        return True
    return False


def open_trade(direction, sl, tp):
    if not connect_mt5():
        return False

    if has_open_position():
        print("⛔ Position déjà ouverte")
        return False

    price = mt5.symbol_info_tick(SYMBOL).ask if direction == "BUY" else mt5.symbol_info_tick(SYMBOL).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": mt5.ORDER_TYPE_BUY if direction == "BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 20250217,
        "comment": "PREDATOR_AUTO",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("❌ Erreur ouverture trade:", result.retcode)
        return False

    print("🚀 Trade ouvert automatiquement")
    return True


def close_position():
    positions = mt5.positions_get(symbol=SYMBOL)
    if not positions:
        return False

    position = positions[0]
    price = mt5.symbol_info_tick(SYMBOL).bid if position.type == 0 else mt5.symbol_info_tick(SYMBOL).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": position.volume,
        "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
        "position": position.ticket,
        "price": price,
        "deviation": 20,
        "magic": 20250217,
        "comment": "PREDATOR_CLOSE",
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("❌ Erreur fermeture:", result.retcode)
        return False

    print("✅ Position fermée")
    return True
