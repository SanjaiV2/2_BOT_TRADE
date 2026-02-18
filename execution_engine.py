import time
from broker_connector import open_trade, close_position
from broker_connector import get_current_price

ACTIVE_POSITION = None

def execute_signal(signal):
    global ACTIVE_POSITION

    if ACTIVE_POSITION is not None:
        print("⚠️ Position already active")
        return

    action = signal["action"]
    sl = signal["sl"]
    tp = signal["tp"]

    ticket = open_trade(action, sl, tp)

    if ticket:
        ACTIVE_POSITION = {
            "ticket": ticket,
            "action": action,
            "sl": sl,
            "tp": tp
        }

        monitor_trade()

def monitor_trade():
    global ACTIVE_POSITION

    while ACTIVE_POSITION is not None:
        bid, ask = get_current_price()
        price = ask if ACTIVE_POSITION["action"] == "BUY" else bid

        if ACTIVE_POSITION["action"] == "BUY":
            if price <= ACTIVE_POSITION["sl"] or price >= ACTIVE_POSITION["tp"]:
                close_position(ACTIVE_POSITION["ticket"])
                ACTIVE_POSITION = None
                print("✅ Trade closed")
                break

        if ACTIVE_POSITION["action"] == "SELL":
            if price >= ACTIVE_POSITION["sl"] or price <= ACTIVE_POSITION["tp"]:
                close_position(ACTIVE_POSITION["ticket"])
                ACTIVE_POSITION = None
                print("✅ Trade closed")
                break

        time.sleep(2)
