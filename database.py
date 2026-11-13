"""SQLite helpers for prediction history (final app target)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent / "data" / "predictions.db"


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                income REAL NOT NULL,
                rent REAL NOT NULL,
                utilities REAL NOT NULL,
                fit_label TEXT NOT NULL,
                leftover REAL NOT NULL,
                housing_share REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_prediction(
    income: float,
    rent: float,
    utilities: float,
    fit_label: str,
    leftover: float,
    housing_share: float,
    db_path: Path | str = DB_PATH,
) -> None:
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO prediction_history
                (income, rent, utilities, fit_label, leftover, housing_share)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (income, rent, utilities, fit_label, leftover, housing_share),
        )
        conn.commit()


def list_predictions(limit: int = 20, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM prediction_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
