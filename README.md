# Rent Affordability Fit Checker

**CIS 3400 | Advanced Programming | Fall 2026 | Project 2**  
**Student:** Antriksh Gupta  
**Option:** 1 — Predictive Web Application

Streamlit app that predicts whether a rental listing fits a budget:

**Comfortable · Stretch · Too High**

…from three inputs (monthly income, rent, utilities), plus estimated leftover cash.

> Deliverable 1 proposal (Word): [`docs/CIS3400_Deliverable1_Rent_Affordability_Gupta.docx`](docs/CIS3400_Deliverable1_Rent_Affordability_Gupta.docx)

---

## Status

| Milestone | Date | Status |
|-----------|------|--------|
| Deliverable 1 — Proposal & design | Nov 16, 2026 | In progress (this repo + proposal doc) |
| Deliverable 2 — Working prototype | Nov 23, 2026 | Planned |
| Deliverable 3 — Final app & presentation | Dec 8, 2026 | Planned |

---

## Problem and users

Students and early-career renters often wonder: *does this apartment fit my budget?*  
This app gives a clear fit label and leftover estimate so users can compare listings quickly.

Results are **planning guidance only**, not financial advice.

---

## Planned features

**Prototype (Nov 23)**
- Inputs: monthly income, monthly rent, monthly utilities
- Output: fit label + estimated leftover
- Load a saved `joblib` model (no retraining in the web app)

**Final (Dec 8)**
- Compare two listings
- SQLite prediction history
- Input validation + edge-case tests
- README run instructions + AI-use disclosure

---

## Architecture

```
[Income, rent, utilities]
          |
          v
   [Streamlit app.py]
          |
          v
 [RentFitPredictor — rent_predictor.py]
   validate → features → load model
          |
          +---> [models/rent_fit_model.joblib]
          |
          v
 [Fit label + leftover $]
          |
          +---> [SQLite via database.py]  (final)
```

| Component | Role |
|-----------|------|
| `notebooks/train_model.ipynb` | Build labeled data, train/evaluate, export joblib |
| `rent_predictor.py` | Validate inputs, compute features, predict |
| `app.py` | Streamlit UI |
| `database.py` | SQLite history helpers (final) |

---

## Tech stack

| Library | Purpose |
|---------|---------|
| Python / pandas | Data prep and features |
| scikit-learn / joblib | Train classifier; save/load model |
| Streamlit | Web UI |
| SQLite | Prediction history (final) |

---

## Project layout

```
rent-affordability-fit-checker/
├── app.py                 # Streamlit UI (prototype+)
├── rent_predictor.py      # Prediction class
├── database.py            # SQLite helpers (final)
├── requirements.txt
├── README.md
├── docs/                  # Deliverable 1 proposal
├── notebooks/             # Model training notebook
├── data/                  # Training data (generated locally)
└── models/                # Saved joblib model
```

---

## Setup (will work after prototype code is added)

```bash
git clone https://github.com/agupta362/rent-affordability-fit-checker.git
cd rent-affordability-fit-checker
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Build plan

| Stage | Focus |
|-------|--------|
| Nov 16 | Proposal + GitHub scaffold |
| Nov 17–19 | Labeled data + train/export model |
| Nov 20–22 | Predictor class + Streamlit form |
| Nov 23 | Prototype: 3 inputs → fit label |
| Nov 24–30 | Compare + SQLite history |
| Dec 1–7 | Tests, polish, README |
| Dec 8 | Final demo + AI disclosure |

---

## AI use plan (Deliverable 1)

I plan to use ChatGPT / Cursor / Copilot for class structure, Streamlit wiring, SQLite helpers, and README wording.  
I own the problem, labeling rules, and architecture. I will review, test, and explain all submitted code.  
A full AI-use disclosure will be added to this README for the final submission.

---

## License / course note

Course project for CIS 3400. Not for commercial use or real lending/rental decisions.
