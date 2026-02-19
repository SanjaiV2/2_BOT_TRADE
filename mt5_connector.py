import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

class MT5Connector:
    """
    Gestionnaire de connexion MT5 et passage d'ordres automatiques
    """
    
    def __init__(self, login, password, server):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
        self.symbol = "XAUUSD"
        
    def connect(self):
        """Connexion à MT5"""
        if not mt5.initialize():
            print(f"❌ Échec initialisation MT5: {mt5.last_error()}")
            return False
        
        # Connexion au compte
        authorized = mt5.login(self.login, password=self.password, server=self.server)
        
        if authorized:
            account_info = mt5.account_info()
            if account_info is not None:
                print(f"✅ Connecté au compte MT5: {account_info.login}")
                print(f"💰 Balance: {account_info.balance} {account_info.currency}")
                print(f"📊 Equity: {account_info.equity} {account_info.currency}")
                self.connected = True
                return True
            else:
                print(f"❌ Erreur info compte: {mt5.last_error()}")
                return False
        else:
            print(f"❌ Échec connexion: {mt5.last_error()}")
            return False
    
    def disconnect(self):
        """Déconnexion propre"""
        mt5.shutdown()
        self.connected = False
        print("🔌 Déconnecté de MT5")
    
    def get_account_info(self):
        """Récupère les infos du compte"""
        if not self.connected:
            return None
        
        account = mt5.account_info()
        if account is None:
            return None
        
        return {
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'free_margin': account.margin_free,
            'profit': account.profit,
            'currency': account.currency
        }
    
    def calculate_lot_size(self, risk_percent=1.0, sl_distance=None):
        """
        Calcule la taille de position basée sur le risque
        risk_percent: % du capital à risquer (par défaut 1%)
        sl_distance: distance du SL en prix
        """
        account = mt5.account_info()
        if account is None:
            return 0.01  # Lot minimum par défaut
        
        balance = account.balance
        risk_amount = balance * (risk_percent / 100)
        
        # Info symbole
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return 0.01
        
        # Si pas de SL distance fourni, utilise 1% du prix
        if sl_distance is None:
            tick_value = symbol_info.trade_tick_value
            lot_size = (risk_amount / (symbol_info.ask * 0.01)) / 100
        else:
            # Calcul avec distance SL réelle
            tick_value = symbol_info.trade_tick_value
            lot_size = risk_amount / (sl_distance * tick_value * 100)
        
        # Arrondir selon lot step
        lot_step = symbol_info.volume_step
        lot_size = round(lot_size / lot_step) * lot_step
        
        # Limites
        lot_min = symbol_info.volume_min
        lot_max = symbol_info.volume_max
        lot_size = max(lot_min, min(lot_size, lot_max))
        
        return lot_size
    
    def send_order(self, order_type, volume, sl=None, tp=None, comment="PREDATOR_AUTO"):
        """
        Envoie un ordre au marché
        order_type: "BUY" ou "SELL"
        volume: taille en lots
        sl: stop loss (prix)
        tp: take profit (prix)
        """
        if not self.connected:
            print("❌ Pas connecté à MT5")
            return None
        
        # Info symbole
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"❌ Symbole {self.symbol} introuvable")
            return None
        
        if not symbol_info.visible:
            if not mt5.symbol_select(self.symbol, True):
                print(f"❌ Impossible de sélectionner {self.symbol}")
                return None
        
        # Prix et type d'ordre
        if order_type == "BUY":
            price = mt5.symbol_info_tick(self.symbol).ask
            order_type_mt5 = mt5.ORDER_TYPE_BUY
        else:  # SELL
            price = mt5.symbol_info_tick(self.symbol).bid
            order_type_mt5 = mt5.ORDER_TYPE_SELL
        
        # Préparation de la requête
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": float(volume),
            "type": order_type_mt5,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Ajout SL/TP si fournis
        if sl is not None:
            request["sl"] = float(sl)
        if tp is not None:
            request["tp"] = float(tp)
        
        # Envoi de l'ordre
        result = mt5.order_send(request)
        
        if result is None:
            print(f"❌ Erreur envoi ordre: {mt5.last_error()}")
            return None
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ Ordre refusé: {result.retcode} - {result.comment}")
            return None
        
        print(f"✅ Ordre exécuté: {order_type} {volume} lots à {price}")
        print(f"   Ticket: {result.order}")
        if sl:
            print(f"   SL: {sl}")
        if tp:
            print(f"   TP: {tp}")
        
        return result
    
    def get_positions(self):
        """Récupère toutes les positions ouvertes"""
        if not self.connected:
            return []
        
        positions = mt5.positions_get(symbol=self.symbol)
        
        if positions is None:
            return []
        
        positions_list = []
        for pos in positions:
            positions_list.append({
                'ticket': pos.ticket,
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'open_price': pos.price_open,
                'current_price': pos.price_current,
                'sl': pos.sl,
                'tp': pos.tp,
                'profit': pos.profit,
                'comment': pos.comment
            })
        
        return positions_list
    
    def close_position(self, ticket):
        """Ferme une position par son ticket"""
        if not self.connected:
            return False
        
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            print(f"❌ Position {ticket} introuvable")
            return False
        
        position = position[0]
        
        # Type d'ordre inverse pour fermer
        if position.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(self.symbol).bid
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).ask
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": position.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": "PREDATOR_CLOSE",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ Échec fermeture position {ticket}")
            return False
        
        print(f"✅ Position {ticket} fermée - Profit: {position.profit}")
        return True
    
    def close_all_positions(self):
        """Ferme toutes les positions ouvertes"""
        positions = self.get_positions()
        for pos in positions:
            self.close_position(pos['ticket'])
        print(f"✅ {len(positions)} position(s) fermée(s)")
    
    def modify_position(self, ticket, new_sl=None, new_tp=None):
        """Modifie le SL/TP d'une position"""
        if not self.connected:
            return False
        
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            return False
        
        position = position[0]
        
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "position": ticket,
        }
        
        if new_sl is not None:
            request["sl"] = float(new_sl)
        else:
            request["sl"] = position.sl
        
        if new_tp is not None:
            request["tp"] = float(new_tp)
        else:
            request["tp"] = position.tp
        
        result = mt5.order_send(request)
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"❌ Échec modification position {ticket}")
            return False
        
        print(f"✅ Position {ticket} modifiée")
        return True