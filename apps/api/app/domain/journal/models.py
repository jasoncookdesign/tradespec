from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    trade_spec_id: str = Field(..., min_length=1)
    exit_price: float = Field(..., gt=0)
    exited_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    outcome_summary: str = Field(..., min_length=3, max_length=500)
    lesson_summary: str = Field(..., min_length=3, max_length=500)


class JournalEntry(JournalEntryCreate):
    id: str = Field(default_factory=lambda: f"journal-{str(uuid4())[:8]}")
    ai_observation: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
