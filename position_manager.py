from mt5_connector import MT5Connector
from datetime import datetime, timedelta
import json
import os

class PositionManager:
    """
    Gestion avancée des positions avec sécurités multiples
    """
    
    def __init__(self, mt5_connector, config_file="trading_config.json"):
        self.mt5 = mt5_connector
        self.config_file = config_file
        self.load_config()
        
        # État interne
        self.daily_trades = 0
        self.daily_profit = 0.0
        self.last_trade_time = None
        self.last_reset_date = datetime.now().date()
    
    def load_config(self):
        """Charge la configuration de trading"""
        default_config = {
            "max_positions": 1,           # Max 1 position simultanée
            "max_daily_trades": 2,        # Max 2 trades par jour
            "risk_per_trade": 1.0,        # 1% du capital par trade
            "max_daily_loss": 3.0,        # Stop trading si -3% de perte journalière
            "max_daily_profit": 6.0,      # Stop trading si +6% de profit journalier (protection)
            "min_cooldown_minutes": 120,  # 2h minimum entre trades
            "trailing_stop_enabled": True,
            "trailing_stop_activation": 1.5,  # Active trailing à +1.5% 
            "trailing_stop_distance": 0.8,    # Trail à 0.8% du prix
            "break_even_enabled": True,
            "break_even_trigger": 1.0,    # Move SL to BE à +1% profit
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def reset_daily_counters(self):
        """Reset les compteurs quotidiens"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_trades = 0
            self.daily_profit = 0.0
            self.last_reset_date = today
            print(f"🔄 Compteurs journaliers réinitialisés")
    
    def can_open_position(self):
        """Vérifie si on peut ouvrir une nouvelle position"""
        self.reset_daily_counters()
        
        reasons = []
        
        # 1. Vérifier nombre de positions actuelles
        positions = self.mt5.get_positions()
        if len(positions) >= self.config['max_positions']:
            reasons.append(f"Max positions atteint ({len(positions)}/{self.config['max_positions']})")
        
        # 2. Vérifier limite trades journaliers
        if self.daily_trades >= self.config['max_daily_trades']:
            reasons.append(f"Max trades journaliers atteint ({self.daily_trades}/{self.config['max_daily_trades']})")
        
        # 3. Vérifier cooldown
        if self.last_trade_time:
            elapsed = (datetime.now() - self.last_trade_time).seconds / 60
            min_cooldown = self.config['min_cooldown_minutes']
            if elapsed < min_cooldown:
                remaining = int(min_cooldown - elapsed)
                reasons.append(f"Cooldown actif ({remaining} min restantes)")
        
        # 4. Vérifier perte journalière max
        account = self.mt5.get_account_info()
        if account:
            daily_loss_pct = (self.daily_profit / account['balance']) * 100
            if daily_loss_pct <= -self.config['max_daily_loss']:
                reasons.append(f"Max perte journalière atteinte ({daily_loss_pct:.2f}%)")
        
        # 5. Vérifier profit journalier max (protection winrate)
        if account:
            daily_profit_pct = (self.daily_profit / account['balance']) * 100
            if daily_profit_pct >= self.config['max_daily_profit']:
                reasons.append(f"Max profit journalier atteint ({daily_profit_pct:.2f}%) - Protection activée")
        
        if reasons:
            return False, " | ".join(reasons)
        
        return True, "OK"
    
    def open_position(self, direction, sl_price, tp_price, signal_info):
        """Ouvre une position avec calcul automatique du lot"""
        can_open, reason = self.can_open_position()
        
        if not can_open:
            print(f"🚫 Position refusée: {reason}")
            return None
        
        # Calcul de la taille de position
        account = self.mt5.get_account_info()
        current_price = self.mt5.mt5.symbol_info_tick(self.mt5.symbol).ask if direction == "BUY" else self.mt5.mt5.symbol_info_tick(self.mt5.symbol).bid
        sl_distance = abs(current_price - sl_price)
        
        lot_size = self.mt5.calculate_lot_size(
            risk_percent=self.config['risk_per_trade'],
            sl_distance=sl_distance
        )
        
        print(f"\n🎯 OUVERTURE POSITION AUTOMATIQUE")
        print(f"   Direction: {direction}")
        print(f"   Prix: {current_price:.2f}")
        print(f"   Lot: {lot_size}")
        print(f"   SL: {sl_price:.2f}")
        print(f"   TP: {tp_price:.2f}")
        print(f"   Risk: {self.config['risk_per_trade']}%")
        print(f"   Signal: {signal_info}\n")
        
        # Envoi de l'ordre
        result = self.mt5.send_order(
            order_type=direction,
            volume=lot_size,
            sl=sl_price,
            tp=tp_price,
            comment=f"SNIPER_{signal_info[:20]}"
        )
        
        if result:
            self.daily_trades += 1
            self.last_trade_time = datetime.now()
            
            # Log
            self.log_trade({
                'timestamp': datetime.now().isoformat(),
                'direction': direction,
                'price': current_price,
                'lot': lot_size,
                'sl': sl_price,
                'tp': tp_price,
                'ticket': result.order,
                'signal': signal_info
            })
            
            return result
        
        return None
    
    def manage_open_positions(self):
        """Gestion active des positions (trailing stop, break even, etc.)"""
        positions = self.mt5.get_positions()
        
        for pos in positions:
            # Break Even
            if self.config['break_even_enabled']:
                self.check_break_even(pos)
            
            # Trailing Stop
            if self.config['trailing_stop_enabled']:
                self.check_trailing_stop(pos)
    
    def check_break_even(self, position):
        """Déplace le SL au point d'entrée si profit suffisant"""
        entry_price = position['open_price']
        current_price = position['current_price']
        sl = position['sl']
        
        if position['type'] == 'BUY':
            profit_pips = current_price - entry_price
            trigger = entry_price * (self.config['break_even_trigger'] / 100)
            
            if profit_pips >= trigger and sl < entry_price:
                # Déplacer SL légèrement au-dessus de BE (pour couvrir spread)
                new_sl = entry_price + (entry_price * 0.0001)
                self.mt5.modify_position(position['ticket'], new_sl=new_sl)
                print(f"✅ Break Even activé sur position {position['ticket']}")
        
        else:  # SELL
            profit_pips = entry_price - current_price
            trigger = entry_price * (self.config['break_even_trigger'] / 100)
            
            if profit_pips >= trigger and sl > entry_price:
                new_sl = entry_price - (entry_price * 0.0001)
                self.mt5.modify_position(position['ticket'], new_sl=new_sl)
                print(f"✅ Break Even activé sur position {position['ticket']}")
    
    def check_trailing_stop(self, position):
        """Active et gère le trailing stop"""
        entry_price = position['open_price']
        current_price = position['current_price']
        sl = position['sl']
        
        if position['type'] == 'BUY':
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            
            if profit_pct >= self.config['trailing_stop_activation']:
                trail_distance = current_price * (self.config['trailing_stop_distance'] / 100)
                new_sl = current_price - trail_distance
                
                if new_sl > sl:
                    self.mt5.modify_position(position['ticket'], new_sl=new_sl)
                    print(f"📈 Trailing stop ajusté: {new_sl:.2f}")
        
        else:  # SELL
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            
            if profit_pct >= self.config['trailing_stop_activation']:
                trail_distance = current_price * (self.config['trailing_stop_distance'] / 100)
                new_sl = current_price + trail_distance
                
                if new_sl < sl:
                    self.mt5.modify_position(position['ticket'], new_sl=new_sl)
                    print(f"📉 Trailing stop ajusté: {new_sl:.2f}")
    
    def update_daily_profit(self):
        """Met à jour le profit journalier"""
        positions = self.mt5.get_positions()
        
        total_profit = sum(pos['profit'] for pos in positions)
        self.daily_profit = total_profit
    
    def log_trade(self, trade_data):
        """Log un trade dans le fichier"""
        log_file = "auto_trades.json"
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                trades = json.load(f)
        else:
            trades = []
        
        trades.append(trade_data)
        
        with open(log_file, 'w') as f:
            json.dump(trades, f, indent=4)
    
    def get_statistics(self):
        """Retourne les statistiques de trading"""
        account = self.mt5.get_account_info()
        positions = self.mt5.get_positions()
        
        return {
            'balance': account['balance'] if account else 0,
            'equity': account['equity'] if account else 0,
            'profit': account['profit'] if account else 0,
            'daily_trades': self.daily_trades,
            'daily_profit': self.daily_profit,
            'open_positions': len(positions),
            'max_daily_trades': self.config['max_daily_trades'],
            'risk_per_trade': self.config['risk_per_trade']
        }