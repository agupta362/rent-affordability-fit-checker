# Testing Evidence — Deliverable 3

**Project:** Rent Affordability Fit Checker  
**Student:** Antriksh Gupta  
**Date:** December 8, 2026

## How to run tests

```bash
cd rent-affordability-fit-checker
python -m unittest tests.test_rent_predictor -v
```

Or:

```bash
python tests/test_rent_predictor.py
```

## Automated test coverage

| Test | What it checks | Expected |
|---|---|---|
| `test_model_file_loads` | `rent_fit_model.joblib` loads | Pass |
| `test_normal_prediction_model_backed` | Normal inputs return label + probabilities | Pass |
| `test_invalid_income_raises` | Income <= 0 rejected | Pass |
| `test_negative_rent_raises` | Negative rent rejected | Pass |
| `test_roommate_share_reduces_rent_burden` | 2 roommates halves rent share / raises leftover | Pass |
| `test_high_eat_out_increases_food_spend` | Often > Rarely food cost in expensive area | Pass |
| `test_stress_test_has_three_rows` | Stress test returns Rarely/Sometimes/Often | Pass |
| `test_gap_advisor_returns_structure` | Advisor dict has required keys | Pass |
| `test_sqlite_save_and_filter` | SQLite save + label/note filter works | Pass |

## Manual UI checks (Streamlit)

| Scenario | Steps | Expected |
|---|---|---|
| Happy path | Defaults → Check rent fit | Money Fit + Place Worth + model success message |
| Invalid income | Set income to 0 → Check | Error message, no crash |
| Stress test | Run prediction | 3-row eat-out table |
| Compare listings | Enable compare → Compare | Side-by-side Fit / leftover / worth |
| History filter | Save a note with “campus” → filter/search | Matching row appears |
| Preset | Choose Intern preset → Check | Inputs fill; prediction runs |

## Model training metrics

See `docs/prototype_metrics.txt` (synthetic labeled data; high accuracy expected because labels follow documented burden rules).

## Known limitations

- Food spend uses documented eat-out × neighborhood bands.
- Synthetic training labels are rule-based for education, not real credit underwriting.
- Results are planning guidance only, not financial advice.
