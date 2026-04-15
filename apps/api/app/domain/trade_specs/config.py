from dataclasses import dataclass


@dataclass(frozen=True)
class TradeValidationConfig:
    minimum_risk_reward_ratio: float = 2.0
    preferred_time_horizon_min_days: int = 3
    preferred_time_horizon_max_days: int = 30


DEFAULT_TRADE_VALIDATION_CONFIG = TradeValidationConfig()
