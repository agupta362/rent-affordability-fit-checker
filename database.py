"""SQLite helpers for decision journal / prediction history."""

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
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                income REAL NOT NULL,
                rent REAL NOT NULL,
                utilities REAL NOT NULL,
                roommates INTEGER NOT NULL,
                eat_out TEXT NOT NULL,
                neighborhood_food_cost TEXT NOT NULL,
                lifestyle_extras REAL NOT NULL,
                neighborhood_quality TEXT NOT NULL,
                unit_condition TEXT NOT NULL,
                food_spend REAL NOT NULL,
                fit_label TEXT NOT NULL,
                place_worth_score INTEGER NOT NULL,
                leftover REAL NOT NULL,
                housing_share REAL NOT NULL,
                burden_share REAL NOT NULL,
                decision_note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_prediction(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> None:
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO prediction_history (
                income, rent, utilities, roommates, eat_out, neighborhood_food_cost,
                lifestyle_extras, neighborhood_quality, unit_condition, food_spend,
                fit_label, place_worth_score, leftover, housing_share, burden_share,
                decision_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["income"],
                payload["rent"],
                payload["utilities"],
                payload["roommates"],
                payload["eat_out"],
                payload["neighborhood_food_cost"],
                payload["lifestyle_extras"],
                payload["neighborhood_quality"],
                payload["unit_condition"],
                payload["food_spend"],
                payload["fit_label"],
                payload["place_worth_score"],
                payload["leftover"],
                payload["housing_share"],
                payload["burden_share"],
                payload.get("decision_note"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def list_predictions(
    limit: int = 50,
    fit_label: str | None = None,
    search_note: str | None = None,
    db_path: Path | str = DB_PATH,
) -> list[dict[str, Any]]:
    init_db(db_path)
    clauses: list[str] = []
    params: list[Any] = []
    if fit_label and fit_label != "All":
        clauses.append("fit_label = ?")
        params.append(fit_label)
    if search_note:
        clauses.append("COALESCE(decision_note, '') LIKE ?")
        params.append(f"%{search_note}%")
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(limit)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            f"""
            SELECT * FROM prediction_history
            {where}
            ORDER BY id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def history_summary(db_path: Path | str = DB_PATH) -> dict[str, Any]:
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        total = conn.execute("SELECT COUNT(*) AS n FROM prediction_history").fetchone()["n"]
        by_label = conn.execute(
            """
            SELECT fit_label, COUNT(*) AS n
            FROM prediction_history
            GROUP BY fit_label
            ORDER BY fit_label
            """
        ).fetchall()
        recent = conn.execute(
            """
            SELECT id, leftover, burden_share, fit_label, created_at
            FROM prediction_history
            ORDER BY id DESC
            LIMIT 20
            """
        ).fetchall()
        return {
            "total": total,
            "by_label": {row["fit_label"]: row["n"] for row in by_label},
            "recent": [dict(row) for row in recent],
        }
    finally:
        conn.close()
