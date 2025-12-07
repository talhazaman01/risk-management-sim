from dataclasses import dataclass
from datetime import datetime
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