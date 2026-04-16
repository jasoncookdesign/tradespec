from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.dependencies import get_journal_service, get_journal_summary_service
from app.domain.ai_services.service import StubAIService
from app.domain.journal.models import JournalEntryCreate
from app.domain.journal.repository import SQLiteJournalRepository
from app.domain.journal.service import JournalPatternSummaryService, JournalService
from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.models import SetupType, TradeSpecInput
from app.domain.trade_specs.repository import SQLiteTradeSpecRepository
from app.domain.trade_specs.service import build_trade_spec
from app.main import app

client = TestClient(app)


def _make_trade(**overrides) -> TradeSpecInput:
    payload = {
        'ticker': 'MSFT',
        'setup_type': SetupType.PULLBACK,
        'entry_zone_min': 100.0,
        'entry_zone_max': 102.0,
        'stop_loss': 95.0,
        'target_price': 112.0,
        'time_horizon_days': 5,
        'thesis': 'Trend pullback into support with defined risk.',
        'ticker_status': EvaluationStatus.VALID,
    }
    payload.update(overrides)
    return TradeSpecInput(**payload)


def test_pattern_summary_handles_insufficient_data(tmp_path: Path) -> None:
    journal_repository = SQLiteJournalRepository(tmp_path / 'journal.sqlite')
    trade_repository = SQLiteTradeSpecRepository(tmp_path / 'trade.sqlite')
    summary_service = JournalPatternSummaryService(journal_repository, trade_repository)

    summary = summary_service.summarize_patterns()

    assert summary.insufficient_data is True
    assert summary.sample_size == 0
    assert len(summary.findings) == 0


def test_pattern_summary_detects_wait_entries_and_early_exits(tmp_path: Path) -> None:
    journal_repository = SQLiteJournalRepository(tmp_path / 'journal.sqlite')
    trade_repository = SQLiteTradeSpecRepository(tmp_path / 'trade.sqlite')
    journal_service = JournalService(journal_repository)
    summary_service = JournalPatternSummaryService(journal_repository, trade_repository)

    first_trade = trade_repository.save(
        build_trade_spec(_make_trade(ticker_status=EvaluationStatus.WAIT))
    )
    first_trade.created_at = datetime.now(UTC) - timedelta(days=8)
    trade_repository.save(first_trade)

    second_trade = trade_repository.save(build_trade_spec(_make_trade(target_price=111.0)))
    second_trade.created_at = datetime.now(UTC) - timedelta(days=9)
    trade_repository.save(second_trade)

    journal_service.create_entry(
        JournalEntryCreate(
            trade_spec_id=first_trade.id,
            exit_price=100.5,
            exited_at=datetime.now(UTC),
            outcome_summary='Exited early from a setup that never fully matured.',
            lesson_summary='Patience was missing.',
        ),
        StubAIService(),
    )
    journal_service.create_entry(
        JournalEntryCreate(
            trade_spec_id=second_trade.id,
            exit_price=101.0,
            exited_at=datetime.now(UTC),
            outcome_summary='Exited before stop but after too much time passed.',
            lesson_summary='Stayed in the trade longer than planned.',
        ),
        StubAIService(),
    )

    summary = summary_service.summarize_patterns()
    titles = [finding.title for finding in summary.findings]

    assert summary.insufficient_data is False
    assert 'Entered WAIT setups' in titles
    assert 'Exited before stop' in titles
    assert 'Expired trades lingered' in titles


def test_pattern_summary_is_deterministic_for_fixed_data(tmp_path: Path) -> None:
    journal_repository = SQLiteJournalRepository(tmp_path / 'journal.sqlite')
    trade_repository = SQLiteTradeSpecRepository(tmp_path / 'trade.sqlite')
    journal_service = JournalService(journal_repository)
    summary_service = JournalPatternSummaryService(journal_repository, trade_repository)

    trade = trade_repository.save(build_trade_spec(_make_trade()))
    trade.created_at = datetime(2026, 1, 1, tzinfo=UTC)
    trade_repository.save(trade)

    journal_service.create_entry(
        JournalEntryCreate(
            trade_spec_id=trade.id,
            exit_price=101.0,
            exited_at=datetime(2026, 1, 10, tzinfo=UTC),
            outcome_summary='Closed the trade.',
            lesson_summary='Stayed mostly disciplined.',
        ),
        StubAIService(),
    )
    journal_service.create_entry(
        JournalEntryCreate(
            trade_spec_id=trade.id,
            exit_price=101.5,
            exited_at=datetime(2026, 1, 11, tzinfo=UTC),
            outcome_summary='Closed another similar trade.',
            lesson_summary='Same pattern repeated.',
        ),
        StubAIService(),
    )

    first = summary_service.summarize_patterns()
    second = summary_service.summarize_patterns()

    assert first.model_dump() == second.model_dump()


def test_journal_summary_endpoint_returns_expected_shape(tmp_path: Path) -> None:
    journal_repository = SQLiteJournalRepository(tmp_path / 'journal.sqlite')
    trade_repository = SQLiteTradeSpecRepository(tmp_path / 'trade.sqlite')
    journal_service = JournalService(journal_repository)
    summary_service = JournalPatternSummaryService(journal_repository, trade_repository)

    app.dependency_overrides[get_journal_service] = lambda: journal_service
    app.dependency_overrides[get_journal_summary_service] = lambda: summary_service

    try:
        response = client.get('/api/journal-summary')
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert 'insufficient_data' in body
    assert 'sample_size' in body
    assert 'findings' in body
