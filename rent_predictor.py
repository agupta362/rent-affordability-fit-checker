"""Rent fit prediction logic (prototype target for Nov 23).

Fit labels: Comfortable | Stretch | Too High
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# joblib / sklearn will be used once the model is trained
# import joblib


MODEL_PATH = Path(__file__).resolve().parent / "models" / "rent_fit_model.joblib"
FIT_LABELS = ("Comfortable", "Stretch", "Too High")


class RentFitPredictor:
    """Validate inputs, build features, and predict rent affordability fit."""

    def __init__(self, model_path: Path | str = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self.model = None  # loaded after training notebook exports joblib

    def load_model(self) -> None:
        """Load the trained classifier from disk."""
        # Placeholder until Deliverable 2:
        # self.model = joblib.load(self.model_path)
        raise NotImplementedError("Train and export rent_fit_model.joblib first (see notebooks/).")

    def validate(self, income: float, rent: float, utilities: float) -> None:
        if income is None or rent is None or utilities is None:
            raise ValueError("Income, rent, and utilities are required.")
        if income <= 0:
            raise ValueError("Monthly income must be positive.")
        if rent < 0 or utilities < 0:
            raise ValueError("Rent and utilities cannot be negative.")

    def features(self, income: float, rent: float, utilities: float) -> dict[str, float]:
        housing = rent + utilities
        return {
            "income": float(income),
            "rent": float(rent),
            "utilities": float(utilities),
            "housing_cost": float(housing),
            "rent_to_income": float(housing / income) if income else 0.0,
            "leftover": float(income - housing),
        }

    def predict(self, income: float, rent: float, utilities: float) -> dict[str, Any]:
        """Return fit label, leftover, and housing share.

        Full model inference comes in the Nov 23 prototype.
        """
        self.validate(income, rent, utilities)
        feats = self.features(income, rent, utilities)

        # Temporary rule-based preview for local testing before the ML model is ready.
        # Replaced by self.model.predict(...) after training.
        ratio = feats["rent_to_income"]
        if ratio <= 0.30:
            label = "Comfortable"
        elif ratio <= 0.40:
            label = "Stretch"
        else:
            label = "Too High"

        return {
            "fit_label": label,
            "leftover": round(feats["leftover"], 2),
            "housing_share": round(ratio, 3),
            "features": feats,
            "model_backed": False,
        }
