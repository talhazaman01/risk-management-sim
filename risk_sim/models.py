# Defines main data types and trade logic

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

class InstrumentType(str, Enum):
    EQUITY = "equity"
    FX = "fx"

@dataclass
class Instrument:
    id: str
    type: InstrumentType
    start_price: float 
    volatility_label: str # low, medium, very_low 

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Trade:
    timestamp: datetime
    instrument_id: str
    side: Side 
    quantity: float 
    price: float 

@dataclass
class Position:
    instrument_id: str
    net_quantity: float = 0.0
    avg_entry_price: float = 0.0 # weighted average 

    def update_with_trade(self, trade: Trade) -> None:
        signed_qty = trade.quantity if trade.side == Side.BUY else -trade.quantity
        new_qty = self.net_quantity + signed_qty

        if new_qty == 0:
            self.net_quantity = 0
            self.avg_entry_price = 0.0
            return

        if (self.net_quantity >= 0 and signed_qty > 0) or (self.net_quantity <= 0 and signed_qty < 0):
            # Adding to existing direction -> recalculate weighted average
            total_value = self.avg_entry_price * abs(self.net_quantity) + trade.price * abs(signed_qty)
            self.net_quantity = new_qty
            self.avg_entry_price = total_value / abs(new_qty)

        else:
            # Reducing or flipping position 
            old_net_quantity = self.net_quantity
            self.net_quantity = new_qty

            # If direction is flipped (crossed zero), set the new average price to the trade price       
            if (old_net_quantity <= 0 and new_qty > 0) or (old_net_quantity > 0 and new_qty < 0):
                self.avg_entry_price = trade.price # resets to the trade price as direction has flipped/stays at trade price if both if & else statements are false

@dataclass
class LimitConfig:
    max_notional_per_instrument: float
    max_gross_notional: float 

class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"

@dataclass
class Alert:
    timestamp: datetime
    severity: AlertSeverity
    type: str 
    message: str 
    details: Optional[Dict[str, float]] = None