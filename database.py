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
                eat_out TEXT NOT NULL,
                neighborhood_food_cost TEXT NOT NULL,
                lifestyle_extras REAL NOT NULL,
                neighborhood_quality TEXT NOT NULL,
                unit_condition TEXT NOT NULL,
                food_spend REAL NOT NULL,
                fit_label TEXT NOT NULL,
                leftover REAL NOT NULL,
                housing_share REAL NOT NULL,
                burden_share REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_prediction(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> None:
    init_db(db_path)
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO prediction_history (
                income, rent, utilities, eat_out, neighborhood_food_cost,
                lifestyle_extras, neighborhood_quality, unit_condition, food_spend,
                fit_label, leftover, housing_share, burden_share
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["income"],
                payload["rent"],
                payload["utilities"],
                payload["eat_out"],
                payload["neighborhood_food_cost"],
                payload["lifestyle_extras"],
                payload["neighborhood_quality"],
                payload["unit_condition"],
                payload["food_spend"],
                payload["fit_label"],
                payload["leftover"],
                payload["housing_share"],
                payload["burden_share"],
            ),
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
