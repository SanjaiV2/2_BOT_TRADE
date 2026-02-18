import MetaTrader5 as mt5
from datetime import datetime

SYMBOL = "XAUUSD"
LOT_SIZE = 0.1

def connect():
    if not mt5.initialize():
        print("❌ MT5 initialization failed")
        return False
    print("✅ MT5 Connected")
    return True

def shutdown():
    mt5.shutdown()

def get_current_price():
    tick = mt5.symbol_info_tick(SYMBOL)
    if tick:
        return tick.bid, tick.ask
    return None, None

def open_trade(action, sl, tp):
    bid, ask = get_current_price()
    if bid is None:
        return None

    price = ask if action == "BUY" else bid
    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "PREDATOR_X_AUTO",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed: {result.retcode}")
        return None

    print(f"🚀 Trade opened at {price}")
    return result.order

def close_position(ticket):
    position = mt5.positions_get(ticket=ticket)
    if not position:
        return False

    position = position[0]
    order_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY

    price = mt5.symbol_info_tick(SYMBOL).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(SYMBOL).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": position.volume,
        "type": order_type,
        "position": position.ticket,
        "price": price,
        "deviation": 20,
        "magic": 123456,
        "comment": "PREDATOR_X_CLOSE",
    }

    result = mt5.order_send(request)
    return result.retcode == mt5.TRADE_RETCODE_DONE
