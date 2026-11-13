# CIS 3400 – Advanced Programming
## Project 2: Python Application Development

**Student Name:** Antriksh Gupta  
**Project Title:** Rent Affordability Fit Checker  
**Course:** CIS 3400 – Advanced Programming  
**Final Presentation:** December 8, 2026

**Deliverable 1 proposal (Word):** [`docs/CIS3400_Deliverable1_Rent_Affordability_Gupta.docx`](docs/CIS3400_Deliverable1_Rent_Affordability_Gupta.docx)

---

## 1. Project Overview

**Application Name:** Rent Affordability Fit Checker

**Project Option:** Predictive ML Application (Option 1 – Predictive Web Application)

### Problem Statement
Students and early-career renters often struggle to judge whether an apartment truly fits their life—not just the rent number. Listing sites show rent and maybe utilities, but they ignore whether someone eats out often, how expensive food is in that neighborhood, lifestyle extras, and whether the area/unit condition is worth the cost. This application predicts a rent-fit label—**Comfortable**, **Stretch**, or **Too High**—using money basics plus lifestyle and neighborhood context, and estimates leftover cash after those costs. Results are planning guidance only, not financial advice.

### Intended Users
Students, interns, and early-career renters comparing apartments. They enter budget and lifestyle details, see a fit label and leftover estimate, and (in the final version) compare listings and review saved checks.

### Unique Features
Unlike classroom ML notebooks or a plain rent calculator, this Streamlit app combines housing costs with personal lifestyle flags (eat-out habits, neighborhood food prices, accessories/extras) and place quality (neighborhood rating, unit condition). A trained classifier turns that into a clear fit decision with history/compare features planned for the final app.

## 2. Application Features

- **Feature 1:** Money inputs — monthly income, rent, utilities.
- **Feature 2:** Lifestyle inputs — eat-out level, neighborhood food cost, monthly extras/accessories; app estimates food spend for that area.
- **Feature 3:** Place inputs — neighborhood quality and apartment/rent condition; these affect the affordability/value judgment.
- **Feature 4:** Output — Comfortable / Stretch / Too High, leftover $, housing share, total burden share, and a short value note.
- **Feature 5 (final):** Compare two listings and save prediction history in SQLite.

Users fill a short grouped form, click **Check rent fit**, and receive a label plus cost breakdown. Final version adds compare + history.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language and application logic |
| Streamlit | Web interface and form-based UI |
| Pandas | Build/clean training examples and feature tables |
| scikit-learn | Train Random Forest (or similar) rent-fit classifier |
| joblib | Save and load the trained model |
| SQLite | Store prediction history (final) |
| Matplotlib | Optional charts of saved prediction history (final) |

## 4. Application Architecture

![Application architecture](docs/architecture.png)

### How the Application Works

1. The user enters money basics, lifestyle/food choices, and neighborhood/unit ratings.
2. The Streamlit interface (`app.py`) passes the values to Python.
3. The `RentFitPredictor` class validates inputs and builds features (housing cost, estimated food spend, extras, burden-to-income, quality scores).
4. The application loads `models/rent_fit_model.joblib` and runs classification inference.
5. The fit label, leftover amount, burden shares, and value note are displayed.
6. In the final version, the result can be saved to SQLite through `database.py`.

Training happens offline in `notebooks/` and exports the joblib file. The web app does not retrain on each prediction.

## 5. Project Structure

```text
rent-affordability-fit-checker/
├── app.py
├── rent_predictor.py
├── database.py
├── requirements.txt
├── README.md
├── models/
│   └── rent_fit_model.joblib          # created after training
├── notebooks/
│   ├── README.md
│   └── train_model_starter.py         # convert/expand to train_model.ipynb
├── data/
│   └── rent_fit_training.csv          # generated locally; not committed
└── docs/
    ├── architecture.png
    ├── CIS3400_Deliverable1_Rent_Affordability_Gupta.docx
    └── DELIVERABLE1_CHECKLIST.md
```

**Important files**
- `app.py` — Streamlit UI (grouped money / lifestyle / place inputs)
- `rent_predictor.py` — `RentFitPredictor` class (validate, features, predict)
- `database.py` — SQLite helpers for history (final)
- `notebooks/train_model_starter.py` — training starter that exports the joblib model
- `docs/architecture.png` — architecture diagram
- `docs/CIS3400_Deliverable1_Rent_Affordability_Gupta.docx` — Deliverable 1 proposal

## 6. Installation and Running the Application

### Step 1: Clone the repository

```bash
git clone https://github.com/agupta362/rent-affordability-fit-checker.git
cd rent-affordability-fit-checker
```

### Step 2: Install dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Train the model (before full ML inference)

```bash
python notebooks/train_model_starter.py
```

This writes `models/rent_fit_model.joblib` and a local training CSV under `data/`.

### Step 4: Run the application

```bash
streamlit run app.py
```

**Notes**
- Current scaffold includes a rule-based preview so the UI runs before the joblib model is fully wired.
- No API keys or secrets are required. Do not commit `.env` files or credentials.

## 7. Testing and Validation

| Test | Expected Result | Actual Result |
|---|---|---|
| Normal inputs (income/rent/utilities + lifestyle defaults) | Fit label + leftover + food estimate | Pending — Deliverable 2 |
| Invalid or missing input (blank / negative values) | Helpful error message | Pending — Deliverable 2 |
| High eat-out + expensive neighborhood food | Higher burden; may move Comfortable → Stretch/Too High | Pending — Deliverable 2 |
| Model interaction after training | Label from saved joblib model | Pending — Deliverable 2 |
| History / compare feature | Saved or compared results display | Pending — final |

**Known limitations (Deliverable 1):** Food spend is estimated from eat-out × neighborhood food-cost bands. Labels use documented synthetic rules. Educational guidance only—not professional financial advice.

## 8. AI-Assisted Development Disclosure

**AI Tools Used:** ChatGPT, Cursor, GitHub Copilot (planned / in use for scaffolding)

### How AI Was Used
AI assistance is planned for class structure, Streamlit form wiring, SQLite helpers, debugging, and README/documentation wording. For Deliverable 1, AI helped draft the proposal structure, repository scaffold, lifestyle-feature design, and architecture wording.

### Student Contributions
I defined the personal rent-fit problem, chose Option 1, expanded inputs to include lifestyle and neighborhood context, planned the architecture (`app.py` → `RentFitPredictor` → joblib → SQLite), and will own labeling rules, integration, testing, and explanation of the final code.

**Student statement:** I reviewed, tested, and can explain the code and technologies used in my application, including code developed with AI assistance.

## 9. Challenges and Lessons Learned

**Challenge 1:** Rent alone is not enough for a personal “can I afford this?” decision.  
**Solution (planned):** Include eat-out habits, neighborhood food cost, extras, neighborhood quality, and unit condition in the feature set and burden calculation.

**Challenge 2:** Keeping the form usable while adding lifestyle context.  
**Solution (planned):** Group inputs into Money / Lifestyle & food / Neighborhood & unit sections with dropdowns for categorical choices.

New skills to develop: packaging a trained model with Streamlit, class-based feature engineering for lifestyle variables, and SQLite history for a small decision app.

## 10. Application Screenshots

Screenshots will be added for Deliverable 2 / final:

1. Main application interface (grouped inputs)
2. Application showing a working prediction result

```markdown
![Main application interface](docs/main-screen.png)
![Prediction result](docs/result-screen.png)
```

## 11. Project Links

**GitHub Repository:** https://github.com/agupta362/rent-affordability-fit-checker  
**Deployed Application:** N/A (local Streamlit for now)  
**Demonstration Video:** N/A (final presentation Dec 8)

## 12. Future Improvements

1. Wire the Streamlit app fully to the trained joblib model (replace preview rules).
2. Add listing compare + SQLite history chart for the final submission.
3. Optional presets (e.g., “student who eats out often”) to speed data entry.

---

### Documentation Timeline

- **Deliverable 1 – November 16:** Complete the project overview, planned features, proposed technologies, preliminary architecture diagram, and planned project structure. These are planning sections and may change as development progresses.
- **Deliverable 2 – November 23:** Update the README to reflect implementation progress and initial testing.
- **Final Deliverable – December 8:** Complete all sections, verify setup instructions, add screenshots, and provide final links.
