# Generates random trades using current prices

import random
from datetime import datetime, timezone
from typing import Dict, Tuple
from .models import Trade, Side

class TradeGenerator:
    def __init__(self, instruments: Dict[str, Tuple[float,float]]):
        """
        instruments: map instrument_id -> (min_qty, max_qty)
        """
        self.instrument_qty_ranges = instruments

    def generate_trade(self, get_price) -> Trade:
        inst_id = random.choice(list(self.instrument_qty_ranges.keys()))
        min_qty, max_qty = self.instrument_qty_ranges[inst_id]
        qty = random.uniform(min_qty, max_qty)
        side = random.choice([Side.BUY, Side.SELL])
        price = get_price(inst_id)

        return Trade(
            timestamp=datetime.now(timezone.utc),
            instrument_id=inst_id,
            side=side,
            quantity=qty,
            price=price
        )