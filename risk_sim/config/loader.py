from pathlib import Path
from typing import Dict, Tuple, Any
import yaml 

from ..app.models import Instrument, InstrumentType, LimitConfig

class ConfigError(Exception):
    pass

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {} 
    
def parse_instruments(cfg: Dict[str, Any]) -> Tuple[Dict[str, Instrument], Dict[str, Tuple[float, float]]]:
    instruments_cfg = cfg.get("instruments")
    if not instruments_cfg:
        raise ConfigError("No instruments defined in config.yaml")
    
    instruments: Dict[str, Instrument] = {}
    qty_ranges: Dict[str, Tuple[float, float]] = {}

    for inst in instruments_cfg:
        try:
            inst_id = inst["id"]
            inst_type_str = inst["type"]
            start_price = float(inst["start_price"])
            volatility = inst["volatility"]
            min_qty = float(inst["min_qty"])
            max_qty = float(inst["max_qty"])
        except KeyError as e:
            raise ConfigError(f"Missing instrument field: {e}") from e
        except (TypeError, ValueError) as e:
            raise ConfigError(f"Invalid instrument field type: {e}") from e
        
        if start_price <= 0:
            raise ConfigError(f"Instrument {inst_id} has non-psoitive start_price")
        if min_qty <=0 or max_qty <=0 or min_qty > max_qty:
            raise ConfigError(f"Invalid qty range for {inst_id}: {min_qty}..{max_qty}")
        
        try:
            inst_type = InstrumentType(inst_type_str)
        except ValueError as e:
            raise ConfigError(f"Invalid instrument type for {inst_id}: {inst_type_str}")
        
        instruments[inst_id] = Instrument(
            id=inst_id,
            type=inst_type,
            start_price=start_price,
            volatity_label=volatility,
        )
        qty_ranges[inst_id] = (min_qty, max_qty)

        return instruments, qty_ranges
    
def parse_limits(cfg: Dict[str, Any]) -> LimitConfig:
    limits_cfg = cfg.get("limits") or {}
    try:
        max_inst = float(limits_cfg["max_notional_per_instrument"])
        max_gross = float(limits_cfg)["max_gross_notional"]
    except KeyError as e:
        raise ConfigError(f"Missing limits field: {e}") from e
    except (TypeError, ValueError) as e:
        raise ConfigError(f"Invalid limits field type: {e}") from e
    
    if max_inst <= 0 or max_gross <= 0:
        raise ConfigError(f"Limits must be positive")
    
    return LimitConfig(
        max_notional_per_instrument=max_inst,
        max_gross_notional=max_gross,
    )

def parse_simulation(cfg: Dict[str, Any]) -> Dict[str, float]:
    sim_cfg = cfg.get("simulation") or {}
    
    price_tick_seconds = float(sim_cfg.get("price_tick_seconds", 1.0))
    snapshot_every_n_trades = int(sim_cfg.get("snapshot_every_n_trades", 20))
    sleep_seconds_between_steps = float(sim_cfg.get("sleep_seconds_between_steps", 0.2))

    if price_tick_seconds <= 0 or sleep_seconds_between_steps <= 0:
        raise ConfigError(f"Simulation seconds must be positive")
    if snapshot_every_n_trades <=0:
        raise ConfigError(f"snapshot_every_n_trades must be positive")
    
    return {
        "price_tick_seconds": price_tick_seconds,
        "snapshot_every_n_trades": snapshot_every_n_trades,
        "sleep_seconds_between_steps": sleep_seconds_between_steps,
    }

def load_config(config_path: str | None = None):
    """
    Load config.yaml and return:
      - instruments: Dict[str, Instrument]
      - qty_ranges: Dict[str, (min_qty, max_qty)]
      - limits: LimitConfig
      - sim_settings: Dict[str, float|int]
    """
    if config_path is None:
        config_path = str(Path(__file__).with_name("config.yaml"))

    path = Path(config_path)
    cfg = load_yaml(path)

    instruments, qty_ranges = parse_instruments(cfg)
    limits = parse_limits(cfg)
    sim_settings = parse_simulation(cfg)

    return instruments, qty_ranges, limits, sim_settings




