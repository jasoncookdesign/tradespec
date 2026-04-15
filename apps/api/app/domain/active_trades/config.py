from dataclasses import dataclass


@dataclass(frozen=True)
class ActiveTradeConfig:
    default_expected_drawdown_min_percent: float = -4.0
    default_expected_drawdown_max_percent: float = -1.5
    expected_time_to_move_min_days_ratio: float = 0.3
    expected_time_to_move_max_days_ratio: float = 0.8
    minimum_progress_pct_before_expiry: float = 1.0


DEFAULT_ACTIVE_TRADE_CONFIG = ActiveTradeConfig()
