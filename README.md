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
Students and early-career renters often struggle to judge whether an apartment truly fits their life—not just the rent number. Typical websites apply a blunt 30% rent rule and ignore eat-out habits, neighborhood food prices, extras, roommates, and whether the area/unit is worth paying for. This application predicts a rent-fit label—**Comfortable**, **Stretch**, or **Too High**—using money basics plus lifestyle and place context, then adds decision tools most calculators lack (dual scores, reverse advice, stress tests). Results are planning guidance only, not financial advice.

### Intended Users
Students, interns, and early-career renters comparing apartments—especially people with roommates or lifestyle spending that a generic calculator misses. They enter budget and lifestyle details, see Money Fit + Place Worth, get “what to change” advice, and (in the final version) save a decision journal.

### Unique Features
This is **not** a classroom penguin/demo notebook and **not** a clone of NerdWallet/Zillow-style rent % calculators. Unique pieces:

1. **Lifestyle-adjusted burden model** — rent + utilities + neighborhood food estimate + extras, not rent-only rules.
2. **Dual score** — **Money Fit** label and a separate **Place Worth** score (neighborhood + unit condition).
3. **Gap-to-Comfortable advisor** — reverse guidance (target rent share, cut eat-out/extras) instead of only scoring current inputs.
4. **Lifestyle stress test** — one-click Rarely vs Sometimes vs Often eat-out comparison for the same listing.
5. **Roommate share mode** — predicts on *your* portion of listed rent.
6. **Student safety-buffer warning** — flags leftover below an emergency monthly target.
7. **Decision journal** (final) — save a personal note with each prediction (why this place matters), beyond anonymous calculator results.

## 2. Application Features

- **Feature 1:** Money inputs — income, listed rent, utilities, people splitting rent.
- **Feature 2:** Lifestyle inputs — eat-out level, neighborhood food cost, extras/accessories; app estimates food spend for that area.
- **Feature 3:** Place inputs — neighborhood quality and apartment condition → Place Worth score.
- **Feature 4:** Dual output — Money Fit + Place Worth, leftover, burden share, value note, safety-buffer alert.
- **Feature 5:** Gap-to-Comfortable advisor and lifestyle stress-test table.
- **Feature 6 (final):** Listing compare + SQLite decision-journal history.

Users fill a grouped form, click **Check rent fit**, and receive dual scores plus advisor/stress-test tools.

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

1. The user enters money basics (including roommates), lifestyle/food choices, place ratings, and an optional journal note.
2. The Streamlit interface (`app.py`) passes the values to Python.
3. The `RentFitPredictor` class validates inputs and builds lifestyle-adjusted features (rent share, food estimate, extras, burden, place worth).
4. The application loads `models/rent_fit_model.joblib` and runs classification inference (preview rules until prototype wiring is complete).
5. Dual scores are shown, then Gap-to-Comfortable tips and an eat-out stress-test table.
6. In the final version, predictions + journal notes are saved through `database.py`.

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
