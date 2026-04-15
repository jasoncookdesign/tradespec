from dataclasses import dataclass


@dataclass(frozen=True)
class PreTradeRuleConfig:
    short_ma_window: int = 20
    long_ma_window: int = 50
    overextension_threshold_pct: float = 0.08
    support_zone_band_pct: float = 0.01
    entry_zone_buffer_pct: float = 0.01
    min_average_daily_volume: int = 1_000_000
    allowed_asset_types: tuple[str, ...] = ("stock", "etf")


DEFAULT_PRETRADE_RULE_CONFIG = PreTradeRuleConfig()
