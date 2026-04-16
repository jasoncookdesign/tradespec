from dataclasses import dataclass


@dataclass(frozen=True)
class PositionSizingConfig:
    default_risk_percent_per_trade: float = 1.0
    minimum_risk_percent_per_trade: float = 0.25
    maximum_risk_percent_per_trade: float = 5.0
    high_capital_utilization_percent: float = 80.0


DEFAULT_POSITION_SIZING_CONFIG = PositionSizingConfig()
