"""Automated tests for Deliverable 3 — Rent Affordability Fit Checker."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import history_summary, list_predictions, save_prediction
from rent_predictor import RentFitPredictor


class RentFitPredictorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.predictor = RentFitPredictor()
        cls.model_ok = cls.predictor.load_model()

    def test_model_file_loads(self) -> None:
        self.assertTrue(self.model_ok, "rent_fit_model.joblib should load for the final app")

    def test_normal_prediction_model_backed(self) -> None:
        result = self.predictor.predict(
            income=4500,
            rent=1800,
            utilities=150,
            eat_out="Sometimes",
            neighborhood_food_cost="Medium",
            lifestyle_extras=100,
            neighborhood_quality="Medium",
            unit_condition="Average",
            roommates=1,
        )
        self.assertIn(result["fit_label"], {"Comfortable", "Stretch", "Too High"})
        self.assertTrue(result["model_backed"])
        self.assertGreaterEqual(result["place_worth_score"], 2)
        self.assertIsNotNone(result["probabilities"])

    def test_invalid_income_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.predictor.predict(income=0, rent=1000, utilities=100, lifestyle_extras=0)

    def test_negative_rent_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.predictor.predict(income=3000, rent=-10, utilities=100, lifestyle_extras=0)

    def test_roommate_share_reduces_rent_burden(self) -> None:
        solo = self.predictor.predict(4500, 2000, 150, "Rarely", "Low", 50, "Medium", "Average", 1)
        shared = self.predictor.predict(4500, 2000, 150, "Rarely", "Low", 50, "Medium", "Average", 2)
        self.assertAlmostEqual(shared["rent_share"], 1000.0)
        self.assertGreater(shared["leftover"], solo["leftover"])

    def test_high_eat_out_increases_food_spend(self) -> None:
        rarely = self.predictor.predict(4500, 1600, 120, "Rarely", "High", 50, "Medium", "Average", 1)
        often = self.predictor.predict(4500, 1600, 120, "Often", "High", 50, "Medium", "Average", 1)
        self.assertGreater(often["food_spend"], rarely["food_spend"])

    def test_stress_test_has_three_rows(self) -> None:
        rows = self.predictor.lifestyle_stress_test(
            4500, 1800, 150, "Medium", 100, "Medium", "Average", 1
        )
        self.assertEqual(len(rows), 3)
        self.assertEqual([r["eat_out"] for r in rows], ["Rarely", "Sometimes", "Often"])

    def test_gap_advisor_returns_structure(self) -> None:
        gap = self.predictor.gap_to_comfortable(
            3000, 2200, 200, "Often", "High", 250, "Low", "Needs work", 1
        )
        self.assertIn("already_comfortable", gap)
        self.assertIn("suggestions", gap)
        self.assertIn("message", gap)

    def test_sqlite_save_and_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.db"
            payload = {
                "income": 4000,
                "rent": 1500,
                "utilities": 100,
                "roommates": 1,
                "eat_out": "Sometimes",
                "neighborhood_food_cost": "Medium",
                "lifestyle_extras": 80,
                "neighborhood_quality": "Medium",
                "unit_condition": "Average",
                "food_spend": 550,
                "fit_label": "Stretch",
                "place_worth_score": 4,
                "leftover": 1770,
                "housing_share": 0.4,
                "burden_share": 0.56,
                "decision_note": "near campus kitchen",
            }
            save_prediction(payload, db_path=db)
            rows = list_predictions(limit=10, fit_label="Stretch", search_note="campus", db_path=db)
            self.assertEqual(len(rows), 1)
            summary = history_summary(db_path=db)
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["by_label"]["Stretch"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
