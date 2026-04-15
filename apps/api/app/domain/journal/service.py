from app.domain.ai_services.service import AIService
from app.domain.journal.models import JournalEntry, JournalEntryCreate
from app.domain.journal.repository import SQLiteJournalRepository


class JournalService:
    def __init__(self, repository: SQLiteJournalRepository):
        self._repository = repository

    def create_entry(self, payload: JournalEntryCreate, ai_service: AIService) -> JournalEntry:
        observation = ai_service.generate_post_trade_observation(
            payload.outcome_summary,
            payload.lesson_summary,
        )
        entry = JournalEntry(
            trade_spec_id=payload.trade_spec_id,
            exit_price=payload.exit_price,
            exited_at=payload.exited_at,
            outcome_summary=payload.outcome_summary,
            lesson_summary=payload.lesson_summary,
            ai_observation=observation,
        )
        return self._repository.save(entry)

    def list_entries(self) -> list[JournalEntry]:
        return self._repository.list_entries()
