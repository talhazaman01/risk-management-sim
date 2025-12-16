# End to end minimal CLI loop to start as a base.

import time
from .models import Instrument, InstrumentType, LimitConfig
from .prices import PriceSimulator
from .trades import TradeGenerator
from .risk import RiskEngine

def main():
    # 1 - Instruments
    
    instruments = {
        "AAPL": Instrument("AAPL", InstrumentType.EQUITY, 200.0, "medium"),
        "MSFT": Instrument("MSFT", InstrumentType.EQUITY, 400.0, "low"),
        "EURUSD": Instrument("EURUSD", InstrumentType.FX, 1.10, "very_low"),
    }

    # 2 - Prices
    price_sim = PriceSimulator(instruments)

    # 3 - Trade generator (min_qty, max_qty)
    trade_gen = TradeGenerator(
        {
            "AAPL": (10, 5000),
            "MSFT": (10,5000),
            "EURUSD": (1000, 10000),
        }
    )

    # 4 - Risk Engine
    limits = LimitConfig(
        max_notional_per_instrument=1000000.0,
        max_gross_notional=2000000.0,
    )

    risk_engine = RiskEngine(limits)

    step = 0
    try:
        while True:
            step +=1

            # Tick prices
            price_sim.tick()
            prices = price_sim.current_prices

            # Generate and process a trade
            trade = trade_gen.generate_trade(price_sim.get_price)
            alerts = risk_engine.process_trade (trade, prices)

            # Occasionally print a summary 
            if step % 20 == 0:
                snap = risk_engine.snapshot(prices)
                print("\n==== SNAPSHOT ====")
                for p in snap["positions"]:
                    print(
                        f"{p['instrument_id']}: qty={p['net_quantity']:.2f}, "
                        f"price={p['current_price']:.4f}, "
                        f"notional={p['notional']:.2f}, pnl={p['pnl']:.2f}"
                    )
                print(
                    f"Gross notional={snap['gross_notional']:.2f}, "
                    f"Total PnL={snap['total_pnl']:.2f}"
                )
                if alerts:
                    print("ALERTS:")
                    for a in alerts:
                        print(f"- [{a.severity.value}] {a.type}: {a.message}")

            time.sleep(0.2) # 5 ticks per second

    except KeyboardInterrupt:
        print("\nStopping simulation.")

if __name__ == "__main__":
    main()