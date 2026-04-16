from app.domain.ai_services.service import AIService
from app.domain.journal.models import (
    JournalEntry,
    JournalEntryCreate,
    JournalPatternFinding,
    JournalPatternSummary,
)
from app.domain.journal.repository import SQLiteJournalRepository
from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.repository import SQLiteTradeSpecRepository


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


class JournalPatternSummaryService:
    def __init__(
        self,
        journal_repository: SQLiteJournalRepository,
        trade_repository: SQLiteTradeSpecRepository,
    ):
        self._journal_repository = journal_repository
        self._trade_repository = trade_repository

    def summarize_patterns(self) -> JournalPatternSummary:
        entries = self._journal_repository.list_entries()
        reviewed = []
        for entry in entries:
            trade = self._trade_repository.get_by_id(entry.trade_spec_id)
            if trade is not None:
                reviewed.append((entry, trade))

        sample_size = len(reviewed)
        if sample_size < 2:
            return JournalPatternSummary(
                insufficient_data=True,
                sample_size=sample_size,
                message='Not enough closed-trade data yet for reliable pattern summaries.',
                findings=[],
            )

        findings: list[JournalPatternFinding] = []

        wait_entries = sum(
            1 for _, trade in reviewed if trade.status == EvaluationStatus.WAIT
        )
        if wait_entries > 0:
            findings.append(
                JournalPatternFinding(
                    key='entered_wait_setups',
                    title='Entered WAIT setups',
                    count=wait_entries,
                    summary=(
                        f'{wait_entries} reviewed trade(s) were entered while the setup '
                        'was still WAIT. Let price come into the entry zone first.'
                    ),
                )
            )

        early_exits = sum(
            1
            for entry, trade in reviewed
            if entry.exit_price > trade.stop_loss and entry.exit_price < trade.target_price
        )
        if early_exits > 0:
            findings.append(
                JournalPatternFinding(
                    key='exited_before_stop',
                    title='Exited before stop',
                    count=early_exits,
                    summary=(
                        f'{early_exits} reviewed trade(s) were closed before the stop was '
                        'hit. Check whether fear overrode the written plan.'
                    ),
                )
            )

        marginal_rr = sum(
            1 for _, trade in reviewed if 2.0 <= trade.risk_reward_ratio <= 2.5
        )
        if marginal_rr > 0:
            findings.append(
                JournalPatternFinding(
                    key='marginal_risk_reward',
                    title='Marginal risk/reward trades',
                    count=marginal_rr,
                    summary=(
                        f'{marginal_rr} reviewed trade(s) used only marginal risk/reward. '
                        'Stronger setups may improve consistency.'
                    ),
                )
            )

        expired_lingers = sum(
            1
            for entry, trade in reviewed
            if (entry.exited_at - trade.created_at).days > trade.time_horizon_days
        )
        if expired_lingers > 0:
            findings.append(
                JournalPatternFinding(
                    key='expired_trades_lingered',
                    title='Expired trades lingered',
                    count=expired_lingers,
                    summary=(
                        f'{expired_lingers} reviewed trade(s) stayed open beyond the '
                        'planned time horizon. Free capital sooner when the setup stalls.'
                    ),
                )
            )

        if not findings:
            return JournalPatternSummary(
                insufficient_data=False,
                sample_size=sample_size,
                message='No recurring issues stand out yet in the reviewed journal data.',
                findings=[],
            )

        return JournalPatternSummary(
            insufficient_data=False,
            sample_size=sample_size,
            message='Pattern summary is based on completed trades linked to saved trade plans.',
            findings=findings[:5],
        )
