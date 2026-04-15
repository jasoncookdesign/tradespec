from typing import Protocol


class AIService(Protocol):
    def critique_trade_note(self, note: str) -> str:
        """Return an advisory-only critique of a journal entry or trade note."""


class StubAIService:
    def critique_trade_note(self, note: str) -> str:
        return f"Advisory stub: review the setup, risk plan, and discipline notes for: {note}"
