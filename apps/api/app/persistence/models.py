from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TradeSpecRecord:
    id: str
    ticker: str
    status: str
    created_at: datetime


@dataclass(slots=True)
class ActiveTradeRecord:
    id: str
    trade_spec_id: str
    guidance_status: str
    entered_at: datetime


@dataclass(slots=True)
class JournalEntryRecord:
    id: str
    trade_spec_id: str
    created_at: datetime
