from typing import Protocol


class AIService(Protocol):
    """Advisory seam only.

    The journal flow currently uses the post-trade observation method.
    Pre-trade summary and critique seams exist for later UI wiring, but they are not
    yet part of the user-facing workflow.
    """

    def summarize_pre_trade(self, setup_context: str) -> str:
        """Return an advisory-only pre-trade summary."""

    def critique_trade(self, trade_note: str) -> str:
        """Return an advisory-only critique of a trade plan or review note."""

    def generate_post_trade_observation(self, outcome_summary: str, lesson_summary: str) -> str:
        """Return an advisory-only post-trade observation."""


class StubAIService:
    def summarize_pre_trade(self, setup_context: str) -> str:
        return (
            'Advisory stub: the setup looks organized for review, but the '
            f'deterministic rules should remain the decision-maker. Context: {setup_context}'
        )

    def critique_trade(self, trade_note: str) -> str:
        return (
            'Advisory stub: review whether the entry, stop, and emotional discipline '
            f'matched the written plan. Notes: {trade_note}'
        )

    def generate_post_trade_observation(self, outcome_summary: str, lesson_summary: str) -> str:
        return (
            'Advisory stub: the outcome suggests reviewing execution quality and '
            f'repeatability. Outcome: {outcome_summary} Lesson: {lesson_summary}'
        )
