# Tracks positions, computes PnL and notional, check limits and returns alerts.

from datetime import datetime
from typing import Dict, List, Tuple
from .models import (
    Position,
    Trade,
    LimitConfig,
    Alert,
    AlertSeverity
)

class RiskEngine:
    def __init__(self, limit_config: LimitConfig):
        self.limit_config = limit_config 
        self.positions: Dict[str, Position] = {}

    def get_or_create_position(self, instrument_id: str) -> Position:
        if instrument_id not in self.positions:
            self.positions[instrument_id] = Position(instrument_id=instrument_id)
        return self.positions[instrument_id]
    
    def process_trade(self, trade: Trade, current_prices: Dict[str,float]) -> List[Alert]:
        pos = self.get_or_create_position(trade.instrument_id)
        pos.update_with_trade(trade)
        return self.check_limits(current_prices)
    
    def check_limits(self, current_prices: Dict[str, float]) -> List[Alert]:
        alerts: List[Alert] = []
        now = datetime.now(datetime.UTC)

        gross_notional = 0.0
        for inst_id, pos in self.positions.items():
            price = current_prices[inst_id]
            notional = abs(pos.net_quantity * price)
            gross_notional += notional # (gross_notional + notional)

            if notional > self.limit_config.max_notional_per_instrument:
                alerts.append(
                    Alert(
                        timestamp=now,
                        severity=AlertSeverity.CRITICAL,
                        type="INSTRUMENT_NOTIONAL_LIMIT",
                        message=f"Instrument {inst_id} notional {notional:2f} exceeds limit",
                        details={"notional": notional},
                    )
                )
        
        if gross_notional > self.limit_config.max_gross_notional:
            alerts.append(
                Alert(
                    timestamp=now,
                    severity=AlertSeverity.WARN,
                    type="GROSS_NOTIONAL_LIMIT",
                    message=f"Gross notional {gross_notional:2f} exceeds limit",
                    details={"gross_notional": gross_notional},
                )
            )

        return alerts
    
    def snapshot(self, current_prices: Dict[str, float]) -> Dict:
        """
        Return a simple view of positions & PnL.
        """
        gross_notional = 0.0
        total_pnl = 0.0
        positions_view: List[Dict] = []

        for inst_id, pos in self.positions.items():
            price = current_prices[inst_id]
            notional = abs(pos.net_quantity * price)
            pnl = (price - pos.avg_entry_price) * pos.net_quantity
            gross_notional += notional 
            total_pnl += pnl 

            positions_view.append(
                {
                    "instrument_id": inst_id,
                    "net_quantity": pos.net_quantity,
                    "avg_entry_price": pos.avg_entry_price,
                    "current_price": price,
                    "notional": notional,
                    "pnl": pnl,
                }
            )

        return {
            "positions": positions_view,
            "gross_notional": gross_notional,
            "total_pnl": total_pnl,
        }

