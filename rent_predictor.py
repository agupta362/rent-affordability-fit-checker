"""Rent fit prediction logic (prototype target for Nov 23).

Fit labels: Comfortable | Stretch | Too High

Accounts for housing costs plus lifestyle and neighborhood context:
eat-out habits, neighborhood food prices, extras/accessories,
neighborhood quality, and unit condition.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

MODEL_PATH = Path(__file__).resolve().parent / "models" / "rent_fit_model.joblib"
FIT_LABELS = ("Comfortable", "Stretch", "Too High")

# Estimated monthly food spend from eat-out level x neighborhood food cost
FOOD_BASE = {
    ("Rarely", "Low"): 250,
    ("Rarely", "Medium"): 320,
    ("Rarely", "High"): 400,
    ("Sometimes", "Low"): 400,
    ("Sometimes", "Medium"): 550,
    ("Sometimes", "High"): 700,
    ("Often", "Low"): 600,
    ("Often", "Medium"): 850,
    ("Often", "High"): 1100,
}

QUALITY_SCORE = {"Low": 1, "Medium": 2, "High": 3}
CONDITION_SCORE = {"Needs work": 1, "Average": 2, "Excellent": 3}
EAT_OUT_SCORE = {"Rarely": 1, "Sometimes": 2, "Often": 3}
FOOD_COST_SCORE = {"Low": 1, "Medium": 2, "High": 3}


class RentFitPredictor:
    """Validate inputs, build features, and predict rent affordability fit."""

    def __init__(self, model_path: Path | str = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self.model = None

    def load_model(self) -> None:
        raise NotImplementedError("Train and export rent_fit_model.joblib first (see notebooks/).")

    def validate(
        self,
        income: float,
        rent: float,
        utilities: float,
        eat_out: str,
        neighborhood_food_cost: str,
        lifestyle_extras: float,
        neighborhood_quality: str,
        unit_condition: str,
    ) -> None:
        if income is None or rent is None or utilities is None:
            raise ValueError("Income, rent, and utilities are required.")
        if income <= 0:
            raise ValueError("Monthly income must be positive.")
        if rent < 0 or utilities < 0 or lifestyle_extras < 0:
            raise ValueError("Rent, utilities, and lifestyle extras cannot be negative.")
        if eat_out not in EAT_OUT_SCORE:
            raise ValueError("Eat-out level must be Rarely, Sometimes, or Often.")
        if neighborhood_food_cost not in FOOD_COST_SCORE:
            raise ValueError("Neighborhood food cost must be Low, Medium, or High.")
        if neighborhood_quality not in QUALITY_SCORE:
            raise ValueError("Neighborhood quality must be Low, Medium, or High.")
        if unit_condition not in CONDITION_SCORE:
            raise ValueError("Unit condition must be Needs work, Average, or Excellent.")

    def estimate_food_spend(self, eat_out: str, neighborhood_food_cost: str) -> float:
        return float(FOOD_BASE[(eat_out, neighborhood_food_cost)])

    def features(
        self,
        income: float,
        rent: float,
        utilities: float,
        eat_out: str,
        neighborhood_food_cost: str,
        lifestyle_extras: float,
        neighborhood_quality: str,
        unit_condition: str,
    ) -> dict[str, float]:
        housing = float(rent + utilities)
        food = self.estimate_food_spend(eat_out, neighborhood_food_cost)
        extras = float(lifestyle_extras)
        total_essentials = housing + food + extras
        return {
            "income": float(income),
            "rent": float(rent),
            "utilities": float(utilities),
            "housing_cost": housing,
            "food_spend": food,
            "lifestyle_extras": extras,
            "total_monthly_burden": total_essentials,
            "rent_to_income": housing / income if income else 0.0,
            "burden_to_income": total_essentials / income if income else 0.0,
            "leftover": float(income - total_essentials),
            "eat_out_score": float(EAT_OUT_SCORE[eat_out]),
            "food_cost_score": float(FOOD_COST_SCORE[neighborhood_food_cost]),
            "neighborhood_quality_score": float(QUALITY_SCORE[neighborhood_quality]),
            "unit_condition_score": float(CONDITION_SCORE[unit_condition]),
        }

    def predict(
        self,
        income: float,
        rent: float,
        utilities: float,
        eat_out: str = "Sometimes",
        neighborhood_food_cost: str = "Medium",
        lifestyle_extras: float = 100.0,
        neighborhood_quality: str = "Medium",
        unit_condition: str = "Average",
    ) -> dict[str, Any]:
        """Return fit label, leftover, and supporting details.

        Preview uses burden-to-income plus light quality adjustments.
        Replaced by joblib model inference in Deliverable 2.
        """
        self.validate(
            income,
            rent,
            utilities,
            eat_out,
            neighborhood_food_cost,
            lifestyle_extras,
            neighborhood_quality,
            unit_condition,
        )
        feats = self.features(
            income,
            rent,
            utilities,
            eat_out,
            neighborhood_food_cost,
            lifestyle_extras,
            neighborhood_quality,
            unit_condition,
        )

        # Burden bands (housing + food + extras) / income
        burden = feats["burden_to_income"]
        if burden <= 0.45:
            label = "Comfortable"
        elif burden <= 0.60:
            label = "Stretch"
        else:
            label = "Too High"

        # If money is only Stretch but place quality is poor, nudge toward Too High.
        # If money is Comfortable and place is strong, keep Comfortable (value note only).
        quality = feats["neighborhood_quality_score"] + feats["unit_condition_score"]
        value_note = "Fair value for the area/condition."
        if label == "Stretch" and quality <= 2:
            label = "Too High"
            value_note = "Budget is tight and neighborhood/unit quality is low."
        elif label == "Comfortable" and quality >= 5:
            value_note = "Strong value: budget fits and neighborhood/unit look solid."
        elif label == "Too High" and quality >= 5:
            value_note = "Nice place, but the total monthly lifestyle cost looks too high."
        elif label == "Stretch":
            value_note = "Doable, but eating out / extras leave less buffer."

        return {
            "fit_label": label,
            "leftover": round(feats["leftover"], 2),
            "housing_share": round(feats["rent_to_income"], 3),
            "burden_share": round(feats["burden_to_income"], 3),
            "food_spend": round(feats["food_spend"], 2),
            "value_note": value_note,
            "features": feats,
            "model_backed": False,
        }
