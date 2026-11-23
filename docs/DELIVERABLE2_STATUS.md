# Deliverable 2 Status — Rent Affordability Fit Checker

**Student:** Antriksh Gupta  
**Date:** November 23, 2026  
**GitHub:** https://github.com/agupta362/rent-affordability-fit-checker

## What I am submitting
1. **Working local prototype** (`streamlit run app.py`)
2. **GitHub repository + README**
3. **Core interaction + integrations:** Form → `RentFitPredictor` → trained joblib model; optional SQLite history
4. **Brief status summary** (this file / README)

Prototype screenshot: `docs/prototype_main_screen.png`

## Run locally
```bash
cd rent-affordability-fit-checker
pip install -r requirements.txt
streamlit run app.py
```

## Completed / working
- Core user interaction (inputs → predict → dual scores / advisor / stress test)
- ML integration: `models/rent_fit_model.joblib`
- SQLite integration: save/list prediction history
- Listing compare (two apartments, same lifestyle)
- Training script + prototype metrics

## Remaining for Dec 8 final
- Stronger history tools (filter/search saved checks; optional trend chart)
- Extra validation/edge-case coverage for unusual roommate and budget combinations
- Small UX polish on compare + journal notes
