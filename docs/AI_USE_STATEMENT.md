# AI Use Statement — Deliverable 3

**Student:** Antriksh Gupta  
**Project:** Rent Affordability Fit Checker  
**Course:** CIS 3400 Advanced Programming  

## AI tools used
ChatGPT, Cursor, and GitHub Copilot

## How AI was used
I used AI to help:
- draft early Streamlit form layout and README structure
- suggest Python class organization for `RentFitPredictor`
- draft SQLite helper patterns
- troubleshoot feature-order mismatches between training and inference
- improve documentation wording for Deliverable 1–3

## What I personally owned / modified
- Problem definition and unique feature set (lifestyle-adjusted fit, dual scoring, stress test, advisor, roommate share, safety buffer, journal)
- Architecture: `app.py` → `RentFitPredictor` → `joblib` model → SQLite
- Labeling rules and synthetic data design
- Aligning training feature columns with inference
- Testing plan, test cases, and verification that model-backed predictions work
- Final presentation content and demo flow

## AI-generated component I tested and modified
The early AI-assisted `RentFitPredictor` / Streamlit scaffold was tested and modified so it:
1. loads `{"model", "features"}` from `rent_fit_model.joblib`
2. builds a feature row in the exact training column order
3. returns class probabilities
4. connects to SQLite history save/filter in the final app

## Student statement
I reviewed, tested, and can explain the code and technologies used in this application, including code developed with AI assistance. I am responsible for the correctness, functionality, and quality of the final submission.
