import sqlite3
from datetime import datetime
from pathlib import Path

from app.domain.journal.models import JournalEntry


class SQLiteJournalRepository:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id TEXT PRIMARY KEY,
                    trade_spec_id TEXT NOT NULL,
                    exit_price REAL NOT NULL,
                    exited_at TEXT NOT NULL,
                    outcome_summary TEXT NOT NULL,
                    lesson_summary TEXT NOT NULL,
                    ai_observation TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def save(self, entry: JournalEntry) -> JournalEntry:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO journal_entries (
                    id,
                    trade_spec_id,
                    exit_price,
                    exited_at,
                    outcome_summary,
                    lesson_summary,
                    ai_observation,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.trade_spec_id,
                    entry.exit_price,
                    entry.exited_at.isoformat(),
                    entry.outcome_summary,
                    entry.lesson_summary,
                    entry.ai_observation,
                    entry.created_at.isoformat(),
                ),
            )
            connection.commit()
        return entry

    def list_entries(self) -> list[JournalEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    trade_spec_id,
                    exit_price,
                    exited_at,
                    outcome_summary,
                    lesson_summary,
                    ai_observation,
                    created_at
                FROM journal_entries
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [
            JournalEntry(
                id=row[0],
                trade_spec_id=row[1],
                exit_price=row[2],
                exited_at=datetime.fromisoformat(row[3]),
                outcome_summary=row[4],
                lesson_summary=row[5],
                ai_observation=row[6],
                created_at=datetime.fromisoformat(row[7]),
            )
            for row in rows
        ]
