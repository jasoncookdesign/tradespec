from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import get_ai_service, get_journal_service
from app.domain.ai_services.service import AIService
from app.domain.journal.models import JournalEntry, JournalEntryCreate
from app.domain.journal.service import JournalService

router = APIRouter(tags=["journal"])


@router.get('/journal-entries', response_model=list[JournalEntry])
def list_journal_entries_route(
    service: Annotated[JournalService, Depends(get_journal_service)],
) -> list[JournalEntry]:
    return service.list_entries()


@router.post("/journal-entry", response_model=JournalEntry)
def create_journal_entry_route(
    payload: JournalEntryCreate,
    ai_service: Annotated[AIService, Depends(get_ai_service)],
    service: Annotated[JournalService, Depends(get_journal_service)],
) -> JournalEntry:
    return service.create_entry(payload, ai_service)
