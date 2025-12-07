import random
from typing import Dict
from .models import Instrument 

VOL_SCALE = {
    "very_low": 0.0005,
    "low": 0.001,
    "medium": 0.002,
}

class PriceSimulator: 
    def __init__(self, instruments: Dict[str, Instrument]):
        self.instruments = instruments
        self.current_prices: Dict[str, float] = {
            inst_id: inst.start_price for inst_id, inst in instruments.items()
        }

    def tick(self) -> None:
        """Advance prices by one step."""
        
        for inst_id, inst in self.instruments.items():
            price = self.current_prices[inst_id]
            vol = VOL_SCALE.get(inst.volatility_label, 0.001)
            
            # Random % change in range [-vol, +vol]
            pct_move = random.uniform(-vol, vol)
            new_price = price * (1 + pct_move)

            # Avoid zero / negative prices
            self.current_prices[inst_id] = max(new_price, 0.01)

    def get_price(self, instrument_id: str) -> float:
        return self.current_prices[instrument_id]
