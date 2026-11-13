"""Starter training script for Deliverable 2.

Labeling idea (document in final notebook):
- Comfortable: housing_cost / income <= 0.30
- Stretch:     0.30 < ratio <= 0.40
- Too High:    ratio > 0.40

Replace/expand with more realistic variation before final submission.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "rent_fit_training.csv"
MODEL_PATH = ROOT / "models" / "rent_fit_model.joblib"


def make_synthetic(n: int = 800, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    income = rng.uniform(2000, 12000, n)
    rent = income * rng.uniform(0.15, 0.55, n)
    utilities = rng.uniform(50, 400, n)
    housing = rent + utilities
    ratio = housing / income
    label = np.where(ratio <= 0.30, "Comfortable", np.where(ratio <= 0.40, "Stretch", "Too High"))
    return pd.DataFrame(
        {
            "income": income,
            "rent": rent,
            "utilities": utilities,
            "housing_cost": housing,
            "rent_to_income": ratio,
            "fit_label": label,
        }
    )


def main() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = make_synthetic()
    df.to_csv(DATA_PATH, index=False)

    feature_cols = ["income", "rent", "utilities", "housing_cost", "rent_to_income"]
    x = df[feature_cols]
    y = df["fit_label"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    print(classification_report(y_test, preds))

    joblib.dump({"model": model, "features": feature_cols}, MODEL_PATH)
    print(f"Saved model -> {MODEL_PATH}")


if __name__ == "__main__":
    main()
