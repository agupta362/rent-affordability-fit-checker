"""Rent fit prediction with lifestyle context and unique decision helpers.

Integrations (Deliverable 2):
- Loads trained scikit-learn model from models/rent_fit_model.joblib
- Optional SQLite history via database.py (used by app)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "models" / "rent_fit_model.joblib"
FIT_LABELS = ("Comfortable", "Stretch", "Too High")

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

COMFORTABLE_BURDEN = 0.45
STRETCH_BURDEN = 0.60
DEFAULT_SAFETY_BUFFER = 300.0

# Must match notebooks/train_model_starter.py FEATURE_COLS
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


class RentFitPredictor:
    """Validate inputs, build features, predict fit, and run unique helpers."""

    def __init__(self, model_path: Path | str = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self.model = None
        self.feature_cols = list(FEATURE_COLS)
        self._load_attempted = False

    def load_model(self) -> bool:
        """Load the trained classifier. Returns True if model is ready."""
        self._load_attempted = True
        if not self.model_path.exists():
            self.model = None
            return False
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.feature_cols = list(payload.get("features", FEATURE_COLS))
        return True

    def ensure_model(self) -> bool:
        if self.model is not None:
            return True
        if not self._load_attempted:
            return self.load_model()
        return False

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
        roommates: int = 1,
    ) -> None:
        if income is None or rent is None or utilities is None:
            raise ValueError("Income, rent, and utilities are required.")
        if income <= 0:
            raise ValueError("Monthly income must be positive.")
        if rent < 0 or utilities < 0 or lifestyle_extras < 0:
            raise ValueError("Rent, utilities, and lifestyle extras cannot be negative.")
        if roommates < 1:
            raise ValueError("Roommates must be at least 1 (you).")
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

    def your_rent_share(self, rent: float, roommates: int) -> float:
        return float(rent) / max(int(roommates), 1)

    def place_worth_score(self, neighborhood_quality: str, unit_condition: str) -> int:
        return QUALITY_SCORE[neighborhood_quality] + CONDITION_SCORE[unit_condition]

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
        roommates: int = 1,
    ) -> dict[str, float]:
        rent_share = self.your_rent_share(rent, roommates)
        housing = rent_share + float(utilities)
        food = self.estimate_food_spend(eat_out, neighborhood_food_cost)
        extras = float(lifestyle_extras)
        total_essentials = housing + food + extras
        worth = self.place_worth_score(neighborhood_quality, unit_condition)
        return {
            "income": float(income),
            "listed_rent": float(rent),
            "rent_share": rent_share,
            "roommates": float(roommates),
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
            "place_worth_score": float(worth),
        }

    def model_feature_row(self, feats: dict[str, float]) -> pd.DataFrame:
        return pd.DataFrame([[feats[c] for c in self.feature_cols]], columns=self.feature_cols)

    def _value_note(self, label: str, feats: dict[str, float]) -> str:
        quality = feats["neighborhood_quality_score"] + feats["unit_condition_score"]
        if label == "Stretch" and quality <= 2:
            return "Budget is tight and neighborhood/unit quality is low."
        if label == "Comfortable" and quality >= 5:
            return "Strong value: budget fits and neighborhood/unit look solid."
        if label == "Too High" and quality >= 5:
            return "Nice place, but the total monthly lifestyle cost looks too high."
        if label == "Stretch":
            return "Doable, but eating out / extras leave less buffer."
        return "Fair value for the area/condition."

    def _rule_label(self, feats: dict[str, float]) -> str:
        burden = feats["burden_to_income"]
        if burden <= COMFORTABLE_BURDEN:
            label = "Comfortable"
        elif burden <= STRETCH_BURDEN:
            label = "Stretch"
        else:
            label = "Too High"
        quality = feats["neighborhood_quality_score"] + feats["unit_condition_score"]
        if label == "Stretch" and quality <= 2:
            label = "Too High"
        return label

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
        roommates: int = 1,
        safety_buffer: float = DEFAULT_SAFETY_BUFFER,
    ) -> dict[str, Any]:
        self.validate(
            income,
            rent,
            utilities,
            eat_out,
            neighborhood_food_cost,
            lifestyle_extras,
            neighborhood_quality,
            unit_condition,
            roommates,
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
            roommates,
        )

        model_backed = self.ensure_model()
        proba = None
        if model_backed and self.model is not None:
            row = self.model_feature_row(feats)
            label = str(self.model.predict(row)[0])
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(row)[0]
                classes = list(self.model.classes_)
                proba = {str(c): float(p) for c, p in zip(classes, probs)}
        else:
            label = self._rule_label(feats)

        value_note = self._value_note(label, feats)
        buffer_ok = feats["leftover"] >= safety_buffer
        buffer_warning = None
        if not buffer_ok:
            buffer_warning = (
                f"Student safety buffer alert: leftover ${feats['leftover']:.0f} "
                f"is below your ${safety_buffer:.0f}/mo emergency target."
            )

        return {
            "fit_label": label,
            "probabilities": proba,
            "place_worth_score": int(feats["place_worth_score"]),
            "place_worth_label": self._worth_label(int(feats["place_worth_score"])),
            "leftover": round(feats["leftover"], 2),
            "housing_share": round(feats["rent_to_income"], 3),
            "burden_share": round(feats["burden_to_income"], 3),
            "food_spend": round(feats["food_spend"], 2),
            "rent_share": round(feats["rent_share"], 2),
            "value_note": value_note,
            "buffer_ok": buffer_ok,
            "buffer_warning": buffer_warning,
            "features": feats,
            "model_backed": model_backed,
        }

    def _worth_label(self, score: int) -> str:
        if score <= 2:
            return "Weak place value"
        if score <= 4:
            return "Average place value"
        return "Strong place value"

    def gap_to_comfortable(
        self,
        income: float,
        rent: float,
        utilities: float,
        eat_out: str,
        neighborhood_food_cost: str,
        lifestyle_extras: float,
        neighborhood_quality: str,
        unit_condition: str,
        roommates: int = 1,
    ) -> dict[str, Any]:
        current = self.predict(
            income,
            rent,
            utilities,
            eat_out,
            neighborhood_food_cost,
            lifestyle_extras,
            neighborhood_quality,
            unit_condition,
            roommates,
        )
        if current["fit_label"] == "Comfortable" and current["buffer_ok"]:
            return {
                "already_comfortable": True,
                "message": "Already in Comfortable range with your safety buffer.",
                "suggestions": [],
            }

        food = self.estimate_food_spend(eat_out, neighborhood_food_cost)
        max_burden = income * COMFORTABLE_BURDEN
        max_rent_share = max(0.0, max_burden - utilities - food - lifestyle_extras)
        max_listed_rent = max_rent_share * roommates
        rarely_food = self.estimate_food_spend("Rarely", neighborhood_food_cost)
        cut_food = max(0.0, food - rarely_food)
        cut_extras_needed = max(
            0.0,
            (rent / roommates + utilities + food + lifestyle_extras) - max_burden,
        )

        suggestions = [
            f"Target your rent share near ${max_rent_share:,.0f}/mo "
            f"(listed rent about ${max_listed_rent:,.0f} with {roommates} person(s)).",
        ]
        if cut_food > 0:
            suggestions.append(
                f"Switch eat-out to Rarely to free about ${cut_food:,.0f}/mo in this neighborhood."
            )
        if lifestyle_extras > 0:
            suggestions.append(
                f"Trim extras/accessories — cutting toward $0 frees up to ${lifestyle_extras:,.0f}/mo "
                f"(about ${cut_extras_needed:,.0f}/mo may be needed from extras/food/rent mix)."
            )
        if current["place_worth_score"] <= 2:
            suggestions.append(
                "Place worth is weak — even a lower rent may not feel worth it unless condition/area improves."
            )

        return {
            "already_comfortable": False,
            "message": "Gap-to-Comfortable advisor (unique reverse guidance).",
            "max_rent_share": round(max_rent_share, 2),
            "max_listed_rent": round(max_listed_rent, 2),
            "suggestions": suggestions,
        }

    def lifestyle_stress_test(
        self,
        income: float,
        rent: float,
        utilities: float,
        neighborhood_food_cost: str,
        lifestyle_extras: float,
        neighborhood_quality: str,
        unit_condition: str,
        roommates: int = 1,
    ) -> list[dict[str, Any]]:
        rows = []
        for level in ("Rarely", "Sometimes", "Often"):
            result = self.predict(
                income,
                rent,
                utilities,
                level,
                neighborhood_food_cost,
                lifestyle_extras,
                neighborhood_quality,
                unit_condition,
                roommates,
            )
            rows.append(
                {
                    "eat_out": level,
                    "fit_label": result["fit_label"],
                    "leftover": result["leftover"],
                    "food_spend": result["food_spend"],
                    "burden_share": result["burden_share"],
                }
            )
        return rows
