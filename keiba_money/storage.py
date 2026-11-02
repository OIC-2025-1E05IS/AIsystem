"""SQLite persistence layer."""

import sqlite3
from pathlib import Path
from typing import Any


class RaceStorage:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS races (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_name TEXT NOT NULL,
                    race_date TEXT NOT NULL,
                    purchase INTEGER NOT NULL CHECK(purchase >= 0),
                    payout INTEGER NOT NULL CHECK(payout >= 0),
                    profit INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def add(self, race_name: str, race_date: str, purchase: int, payout: int) -> int:
        profit = payout - purchase
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO races (race_name, race_date, purchase, payout, profit) VALUES (?, ?, ?, ?, ?)",
                (race_name.strip(), race_date, purchase, payout, profit),
            )
            return int(cursor.lastrowid)

    def list_all(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, race_name, race_date, purchase, payout, profit FROM races ORDER BY race_date DESC, id DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def totals(self) -> dict[str, int | float]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(SUM(purchase), 0) AS purchase, COALESCE(SUM(payout), 0) AS payout, "
                "COALESCE(SUM(profit), 0) AS profit FROM races"
            ).fetchone()
        purchase, payout = int(row["purchase"]), int(row["payout"])
        rate = payout / purchase * 100 if purchase else 0.0
        return {"purchase": purchase, "payout": payout, "profit": int(row["profit"]), "recovery_rate": rate}

    def delete(self, race_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM races WHERE id = ?", (race_id,))
            return cursor.rowcount > 0
