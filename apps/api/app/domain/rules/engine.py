from datetime import UTC, datetime

from app.domain.evaluations.models import AssetType, PriceZone, TickerEvaluation
from app.domain.market_data.models import MarketSnapshot
from app.domain.rules.config import DEFAULT_PRETRADE_RULE_CONFIG, PreTradeRuleConfig
from app.domain.rules.models import EvaluationStatus


def _moving_average(values: list[float], window: int) -> float:
    return sum(values[-window:]) / window


def _build_preferred_zones(
    recent_closes: list[float],
    short_ma: float,
    config: PreTradeRuleConfig,
) -> tuple[PriceZone, PriceZone]:
    """Build the preferred support zone and the slightly wider entry zone.

    The support zone anchors to the recent pullback area while the entry zone allows
    a small buffer above support so the user is not forced to buy the exact low tick.
    """

    preferred_support_reference = max(sum(recent_closes[-5:]) / 5, short_ma)
    preferred_support_zone = PriceZone(
        min_price=round(
            preferred_support_reference * (1 - config.support_zone_band_pct),
            2,
        ),
        max_price=round(
            preferred_support_reference * (1 + config.support_zone_band_pct),
            2,
        ),
    )
    preferred_entry_zone = PriceZone(
        min_price=preferred_support_zone.min_price,
        max_price=round(
            preferred_support_zone.max_price * (1 + config.entry_zone_buffer_pct),
            2,
        ),
    )
    return preferred_support_zone, preferred_entry_zone


def evaluate_market_snapshot(
    snapshot: MarketSnapshot,
    config: PreTradeRuleConfig = DEFAULT_PRETRADE_RULE_CONFIG,
) -> TickerEvaluation:
    closes = snapshot.historical_closes
    ma20 = _moving_average(closes, config.short_ma_window)
    ma50 = _moving_average(closes, config.long_ma_window)
    recent_closes = [bar.close for bar in snapshot.recent_bars]
    preferred_support_zone, preferred_entry_zone = _build_preferred_zones(
        recent_closes,
        ma20,
        config,
    )

    momentum_return_pct = ((snapshot.current_price - closes[-6]) / closes[-6]) * 100
    average_daily_range_pct = (
        sum(((bar.high - bar.low) / bar.close) * 100 for bar in snapshot.recent_bars)
        / len(snapshot.recent_bars)
    )
    average_volume = int(sum(snapshot.volumes[-20:]) / 20) if snapshot.volumes else 0
    extension_above_ma20_pct = (snapshot.current_price - ma20) / ma20

    is_above_entry_zone = snapshot.current_price > preferred_entry_zone.max_price
    is_below_support_zone = snapshot.current_price < preferred_support_zone.min_price
    is_in_pullback_zone = (
        preferred_support_zone.min_price
        <= snapshot.current_price
        <= preferred_entry_zone.max_price
    )

    reasons: list[str] = []
    asset_type_value = snapshot.asset_type.lower()

    if asset_type_value in {AssetType.STOCK.value, AssetType.ETF.value}:
        asset_type = AssetType(asset_type_value)
    else:
        asset_type = AssetType.UNKNOWN

    if asset_type_value not in config.allowed_asset_types:
        reasons.append("Unsupported asset type for the MVP universe.")
        status = EvaluationStatus.INVALID
    elif average_volume < config.min_average_daily_volume:
        reasons.append("Average trading volume is too light for the liquid-universe filter.")
        status = EvaluationStatus.INVALID
    elif snapshot.current_price <= ma20 or snapshot.current_price <= ma50:
        reasons.append("Price is below the required 20-day or 50-day trend baseline.")
        status = EvaluationStatus.INVALID
    elif extension_above_ma20_pct > config.overextension_threshold_pct:
        reasons.append("Price is extended above trend support and may be too easy to chase here.")
        status = EvaluationStatus.WAIT
    elif is_above_entry_zone:
        reasons.append(
            "Price is still above the preferred pullback zone, so patience is warranted."
        )
        status = EvaluationStatus.WAIT
    elif is_below_support_zone:
        reasons.append(
            "Price has slipped below the preferred support zone and should reclaim it before entry."
        )
        status = EvaluationStatus.WAIT
    elif is_in_pullback_zone:
        reasons.append("Trend, liquidity, and entry location satisfy the current rule set.")
        status = EvaluationStatus.VALID
    else:
        reasons.append("Setup is close, but it is not yet in the preferred pullback area.")
        status = EvaluationStatus.WAIT

    trend_position = (
        "above"
        if snapshot.current_price > ma20 and snapshot.current_price > ma50
        else "below"
    )
    trend_summary = (
        f"Price is {trend_position} the {config.short_ma_window}-day and "
        f"{config.long_ma_window}-day moving averages."
    )
    momentum_summary = (
        f"Recent momentum is {'positive' if momentum_return_pct >= 0 else 'negative'} "
        f"at {momentum_return_pct:.1f}%."
    )
    if is_in_pullback_zone:
        structure_summary = "Structure is sitting in the preferred pullback zone."
    elif is_above_entry_zone:
        structure_summary = "Structure is above the preferred entry zone and looks chase-prone."
    else:
        structure_summary = "Structure is below the preferred support zone and needs reclamation."
    volatility_label = (
        "contained" if average_daily_range_pct < 3.5 else "somewhat elevated"
    )
    volatility_summary = (
        f"Average recent daily range is {average_daily_range_pct:.1f}%, which is "
        f"{volatility_label} for a swing setup."
    )

    return TickerEvaluation(
        ticker=snapshot.ticker,
        asset_type=asset_type,
        trend_summary=trend_summary,
        momentum_summary=momentum_summary,
        structure_summary=structure_summary,
        volatility_summary=volatility_summary,
        status=status,
        reasons=reasons,
        suggested_entry_zone=preferred_entry_zone,
        suggested_support_zone=preferred_support_zone,
        generated_at=datetime.now(UTC),
    )
