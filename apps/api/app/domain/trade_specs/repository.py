import sqlite3
from pathlib import Path

from app.domain.rules.models import EvaluationStatus
from app.domain.trade_specs.models import TradeSpec


class SQLiteTradeSpecRepository:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS trade_specs (
                    id TEXT PRIMARY KEY,
                    ticker TEXT NOT NULL,
                    setup_type TEXT NOT NULL,
                    entry_zone_min REAL NOT NULL,
                    entry_zone_max REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    target_price REAL NOT NULL,
                    time_horizon_days INTEGER NOT NULL,
                    thesis TEXT NOT NULL,
                    risk_reward_ratio REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(self, trade_spec: TradeSpec) -> TradeSpec:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO trade_specs (
                    id, ticker, setup_type, entry_zone_min, entry_zone_max,
                    stop_loss, target_price, time_horizon_days, thesis,
                    risk_reward_ratio, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    trade_spec.id,
                    trade_spec.ticker,
                    trade_spec.setup_type.value,
                    trade_spec.entry_zone_min,
                    trade_spec.entry_zone_max,
                    trade_spec.stop_loss,
                    trade_spec.target_price,
                    trade_spec.time_horizon_days,
                    trade_spec.thesis,
                    trade_spec.risk_reward_ratio,
                    trade_spec.status.value,
                    trade_spec.created_at.isoformat(),
                ),
            )
        return trade_spec

    def get_by_id(self, trade_id: str) -> TradeSpec | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, ticker, setup_type, entry_zone_min, entry_zone_max, stop_loss, "
                "target_price, time_horizon_days, thesis, risk_reward_ratio, status, created_at "
                "FROM trade_specs WHERE id = ?",
                (trade_id,),
            ).fetchone()

        if row is None:
            return None

        return TradeSpec(
            id=row[0],
            ticker=row[1],
            setup_type=row[2],
            entry_zone_min=row[3],
            entry_zone_max=row[4],
            stop_loss=row[5],
            target_price=row[6],
            time_horizon_days=row[7],
            thesis=row[8],
            risk_reward_ratio=row[9],
            status=EvaluationStatus(row[10]),
            created_at=row[11],
        )
