from pathlib import Path

from fastapi.testclient import TestClient

from app.domain.ai_services.service import StubAIService
from app.domain.journal.models import JournalEntryCreate
from app.domain.journal.repository import SQLiteJournalRepository
from app.domain.journal.service import JournalService
from app.main import app

client = TestClient(app)


def _make_payload() -> JournalEntryCreate:
    return JournalEntryCreate(
        trade_spec_id='trade-msft-001',
        exit_price=111.5,
        outcome_summary='Closed into planned strength.',
        lesson_summary='Following the plan reduced emotional exits.',
    )


def test_journal_repository_persists_and_lists_entries(tmp_path: Path) -> None:
    repository = SQLiteJournalRepository(tmp_path / 'journal.sqlite')
    service = JournalService(repository)

    created = service.create_entry(_make_payload(), StubAIService())
    entries = service.list_entries()

    assert created.trade_spec_id == 'trade-msft-001'
    assert len(entries) == 1
    assert entries[0].id == created.id


def test_journal_routes_support_create_and_list() -> None:
    create_response = client.post(
        '/api/journal-entry',
        json={
            'trade_spec_id': 'trade-msft-002',
            'exit_price': 112.25,
            'outcome_summary': 'Took profits into resistance.',
            'lesson_summary': 'Patience improved the outcome.',
        },
    )
    list_response = client.get('/api/journal-entries')

    assert create_response.status_code == 200
    assert 'ai_observation' in create_response.json()
    assert list_response.status_code == 200
    assert any(
        entry['trade_spec_id'] == 'trade-msft-002' for entry in list_response.json()
    )


def test_stub_ai_service_returns_advisory_only_content() -> None:
    ai_service = StubAIService()

    assert 'Advisory' in ai_service.summarize_pre_trade('Pullback into support')
    assert 'Advisory' in ai_service.critique_trade('Risk plan respected stop placement')
    assert 'Advisory' in ai_service.generate_post_trade_observation(
        'Closed green',
        'Discipline was solid',
    )


def test_journal_flow_does_not_require_live_ai_api(tmp_path: Path) -> None:
    repository = SQLiteJournalRepository(tmp_path / 'journal.sqlite')
    service = JournalService(repository)

    entry = service.create_entry(_make_payload(), StubAIService())

    assert entry.ai_observation.startswith('Advisory')
