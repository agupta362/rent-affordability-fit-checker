# Final Presentation Script (~7–8 minutes)

**Student:** Antriksh Gupta  
**App:** Rent Affordability Fit Checker  
**Exam slot:** Tuesday, December 8, 2026 (11:30 am–2:30 pm)

---

## 1) Demo of core functionality (3–5 min)

“Hi, my project is the Rent Affordability Fit Checker, Option 1.

Most rent calculators only use a 30% rule. Mine also includes lifestyle: eating out, neighborhood food cost, extras, roommates, neighborhood quality, and unit condition.

I’ll run it locally with Streamlit.”

*(Open app — confirm green banner that model is loaded.)*

“I enter income, rent, utilities, and lifestyle settings, then click **Check rent fit**.

The app returns:
- **Money Fit** — Comfortable, Stretch, or Too High from the trained model  
- **Place Worth** score  
- leftover money, food estimate, burden share  
- Gap-to-Comfortable tips  
- eat-out stress test table  

I can also save a journal note to SQLite, filter history, and compare two listings.”

---

## 2) Code / architecture / integrations (1–2 min)

“Pipeline:
**Streamlit `app.py` → `RentFitPredictor` → `rent_fit_model.joblib` → results → optional SQLite `database.py`.**

The class validates inputs, derives features like rent share and food spend, then calls the Random Forest model. Training happens offline in `notebooks/train_model_starter.py`; the web app does not retrain.”

---

## 3) Testing, challenges, AI (≈1 min)

“I wrote automated tests in `tests/test_rent_predictor.py` for model loading, validation errors, roommate share, stress test, and SQLite filters. Evidence is in `docs/TESTING.md`.

One challenge was keeping feature order identical between training and inference — I fixed that by exporting the feature list with the joblib file.

I used AI to help scaffold Streamlit and class structure, then tested and modified the code for model loading, probabilities, and SQLite history. I can explain the full pipeline.”

---

## Close

“GitHub: https://github.com/agupta362/rent-affordability-fit-checker — happy to take questions.”
