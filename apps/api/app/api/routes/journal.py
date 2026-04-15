from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_ai_service
from app.domain.ai_services.service import AIService
from app.domain.journal.models import JournalEntry, JournalEntryCreate
from app.domain.journal.service import JournalService

router = APIRouter(tags=["journal"])
service = JournalService()


@router.get('/journal-entries', response_model=list[JournalEntry])
def list_journal_entries_route() -> list[JournalEntry]:
    return service.list_entries()


@router.post("/journal-entry", response_model=JournalEntry)
def create_journal_entry_route(
    payload: JournalEntryCreate,
    ai_service: Annotated[AIService, Depends(get_ai_service)],
) -> JournalEntry:
    return service.create_entry(payload, ai_service)
