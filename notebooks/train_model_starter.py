"""Train and export the rent-fit classifier for Deliverable 2.

Synthetic rows use documented labeling rules:
- Comfortable: burden_to_income <= 0.45
- Stretch: 0.45 < burden_to_income <= 0.60
- Too High: burden_to_income > 0.60
- Nudge: Stretch + weak place worth (quality+condition <= 2) -> Too High

Feature column order must match RentFitPredictor.model_feature_row().
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "rent_fit_training.csv"
MODEL_PATH = ROOT / "models" / "rent_fit_model.joblib"
METRICS_PATH = ROOT / "docs" / "prototype_metrics.txt"

FOOD_BASE = {
    (1, 1): 250,
    (1, 2): 320,
    (1, 3): 400,
    (2, 1): 400,
    (2, 2): 550,
    (2, 3): 700,
    (3, 1): 600,
    (3, 2): 850,
    (3, 3): 1100,
}

FEATURE_COLS = [
    "income",
    "rent_share",
    "utilities",
    "housing_cost",
    "food_spend",
    "lifestyle_extras",
    "total_monthly_burden",
    "rent_to_income",
    "burden_to_income",
    "eat_out_score",
    "food_cost_score",
    "neighborhood_quality_score",
    "unit_condition_score",
    "place_worth_score",
]


def make_synthetic(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    income = rng.uniform(2200, 12000, n)
    roommates = rng.integers(1, 4, n)
    listed_rent = income * rng.uniform(0.18, 0.55, n)
    rent_share = listed_rent / roommates
    utilities = rng.uniform(50, 350, n)
    eat_out_score = rng.integers(1, 4, n)
    food_cost_score = rng.integers(1, 4, n)
    lifestyle_extras = rng.uniform(0, 400, n)
    neighborhood_quality_score = rng.integers(1, 4, n)
    unit_condition_score = rng.integers(1, 4, n)

    food_spend = np.array(
        [FOOD_BASE[(int(e), int(f))] for e, f in zip(eat_out_score, food_cost_score)]
    )
    housing = rent_share + utilities
    burden = housing + food_spend + lifestyle_extras
    burden_ratio = burden / income
    place_worth_score = neighborhood_quality_score + unit_condition_score

    label = np.where(
        burden_ratio <= 0.45,
        "Comfortable",
        np.where(burden_ratio <= 0.60, "Stretch", "Too High"),
    )
    label = np.where((label == "Stretch") & (place_worth_score <= 2), "Too High", label)

    return pd.DataFrame(
        {
            "income": income,
            "listed_rent": listed_rent,
            "roommates": roommates,
            "rent_share": rent_share,
            "utilities": utilities,
            "housing_cost": housing,
            "food_spend": food_spend,
            "lifestyle_extras": lifestyle_extras,
            "total_monthly_burden": burden,
            "rent_to_income": housing / income,
            "burden_to_income": burden_ratio,
            "eat_out_score": eat_out_score,
            "food_cost_score": food_cost_score,
            "neighborhood_quality_score": neighborhood_quality_score,
            "unit_condition_score": unit_condition_score,
            "place_worth_score": place_worth_score,
            "fit_label": label,
        }
    )


def main() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = make_synthetic()
    df.to_csv(DATA_PATH, index=False)

    x = df[FEATURE_COLS]
    y = df["fit_label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=120, random_state=42)
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    report = classification_report(y_test, preds)
    acc = accuracy_score(y_test, preds)
    print(report)
    print(f"Accuracy: {acc:.3f}")

    joblib.dump({"model": model, "features": FEATURE_COLS}, MODEL_PATH)
    METRICS_PATH.write_text(
        f"Deliverable 2 prototype model metrics\n"
        f"Rows: {len(df)}\n"
        f"Accuracy: {acc:.3f}\n\n"
        f"{report}\n",
        encoding="utf-8",
    )
    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved metrics -> {METRICS_PATH}")


if __name__ == "__main__":
    main()
