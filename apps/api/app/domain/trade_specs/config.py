from dataclasses import dataclass


@dataclass(frozen=True)
class TradeValidationConfig:
    minimum_risk_reward_ratio: float = 2.0
    weak_risk_reward_ratio_ceiling: float = 2.5
    strong_risk_reward_ratio_floor: float = 3.5
    accepted_time_horizon_min_days: int = 3
    accepted_time_horizon_max_days: int = 30
    max_stop_distance_percent: float = 8.0
    max_entry_zone_width_percent: float = 2.0


DEFAULT_TRADE_VALIDATION_CONFIG = TradeValidationConfig()
