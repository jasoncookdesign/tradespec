from math import floor

from app.domain.position_sizing.config import DEFAULT_POSITION_SIZING_CONFIG, PositionSizingConfig
from app.domain.position_sizing.models import (
    PositionSizingRequest,
    PositionSizingResult,
    PositionSizingStatus,
)
from app.domain.trade_specs.service import validate_trade


def _derive_entry_price(request: PositionSizingRequest) -> float:
    return round(request.intended_entry_price, 2)


def calculate_position_size(
    request: PositionSizingRequest,
    config: PositionSizingConfig = DEFAULT_POSITION_SIZING_CONFIG,
) -> PositionSizingResult:
    validation = validate_trade(request.trade)
    entry_price = _derive_entry_price(request)
    risk_dollars = round(
        request.account_size_dollars * (request.risk_percent_per_trade / 100),
        2,
    )
    risk_per_share = round(entry_price - request.trade.stop_loss, 2)

    notes: list[str] = []
    warnings: list[str] = []

    notes.append('Position sizing used the explicit intended entry price you provided.')

    if not validation.approved:
        warnings.append('Only approved trades may be sized. Review the trade validation first.')
        warnings.extend(validation.reasons[:2])
        return PositionSizingResult(
            approved_for_sizing=False,
            status=PositionSizingStatus.BLOCKED,
            account_size_dollars=request.account_size_dollars,
            risk_percent_per_trade=request.risk_percent_per_trade,
            entry_price_used=entry_price,
            risk_dollars=risk_dollars,
            risk_per_share=risk_per_share,
            suggested_shares=0,
            capital_required=0.0,
            capital_utilization_percent=0.0,
            notes=notes,
            warnings=warnings,
        )

    if risk_per_share <= 0:
        warnings.append('Risk per share must be positive. Entry price must stay above the stop.')
        return PositionSizingResult(
            approved_for_sizing=False,
            status=PositionSizingStatus.BLOCKED,
            account_size_dollars=request.account_size_dollars,
            risk_percent_per_trade=request.risk_percent_per_trade,
            entry_price_used=entry_price,
            risk_dollars=risk_dollars,
            risk_per_share=risk_per_share,
            suggested_shares=0,
            capital_required=0.0,
            capital_utilization_percent=0.0,
            notes=notes,
            warnings=warnings,
        )

    suggested_shares = floor(risk_dollars / risk_per_share)
    notes.append('Suggested shares are always floored to avoid exceeding the risk budget.')
    capital_required = round(suggested_shares * entry_price, 2)
    capital_utilization_percent = round(
        (capital_required / request.account_size_dollars) * 100,
        2,
    )

    if suggested_shares < 1:
        warnings.append(
            'The allowed dollar risk is too small for even one share at this setup risk.'
        )
        return PositionSizingResult(
            approved_for_sizing=False,
            status=PositionSizingStatus.BLOCKED,
            account_size_dollars=request.account_size_dollars,
            risk_percent_per_trade=request.risk_percent_per_trade,
            entry_price_used=entry_price,
            risk_dollars=risk_dollars,
            risk_per_share=risk_per_share,
            suggested_shares=0,
            capital_required=0.0,
            capital_utilization_percent=0.0,
            notes=notes,
            warnings=warnings,
        )

    if not request.trade.entry_zone_min <= entry_price <= request.trade.entry_zone_max:
        warnings.append('The intended entry price is outside the preferred entry zone.')

    if capital_required > request.account_size_dollars:
        warnings.append(
            'The trade setup is valid, but this share count is not feasible '
            'for the current account size.'
        )
        notes.append('Sizing assumes a cash account with no leverage.')
        return PositionSizingResult(
            approved_for_sizing=False,
            status=PositionSizingStatus.NOT_FEASIBLE,
            account_size_dollars=request.account_size_dollars,
            risk_percent_per_trade=request.risk_percent_per_trade,
            entry_price_used=entry_price,
            risk_dollars=risk_dollars,
            risk_per_share=risk_per_share,
            suggested_shares=suggested_shares,
            capital_required=capital_required,
            capital_utilization_percent=capital_utilization_percent,
            notes=notes,
            warnings=warnings,
        )

    if capital_utilization_percent >= config.high_capital_utilization_percent:
        warnings.append(
            'This position uses a large share of the account, even though '
            'the risk amount is within limits.'
        )

    notes.append(
        'Position sizing is deterministic and based only on account risk, '
        'entry price, and stop loss.'
    )

    return PositionSizingResult(
        approved_for_sizing=True,
        status=PositionSizingStatus.READY,
        account_size_dollars=request.account_size_dollars,
        risk_percent_per_trade=request.risk_percent_per_trade,
        entry_price_used=entry_price,
        risk_dollars=risk_dollars,
        risk_per_share=risk_per_share,
        suggested_shares=suggested_shares,
        capital_required=capital_required,
        capital_utilization_percent=capital_utilization_percent,
        notes=notes,
        warnings=warnings,
    )
