from app.domain.ai_services.service import AIService
from app.domain.journal.models import JournalEntry, JournalEntryCreate


class JournalService:
    def create_entry(self, payload: JournalEntryCreate, ai_service: AIService) -> JournalEntry:
        observation = ai_service.critique_trade_note(
            f"Outcome: {payload.outcome_summary} Lesson: {payload.lesson_summary}"
        )
        return JournalEntry(
            trade_spec_id=payload.trade_spec_id,
            exit_price=payload.exit_price,
            exited_at=payload.exited_at,
            outcome_summary=payload.outcome_summary,
            lesson_summary=payload.lesson_summary,
            ai_observation=observation,
        )
