# CIS 3400 – Advanced Programming
## Project 2: Python Application Development

**Student Name:** Antriksh Gupta  
**Project Title:** Rent Affordability Fit Checker  
**Course:** CIS 3400 – Advanced Programming  
**Final Presentation:** December 8, 2026

**Deliverable 1 status:** Resubmission for full credit — README updated with clearer architecture, interface sketch, prototype vs final scope, module roles, and AI-assisted development workflow.

---

## 1. Project Overview

**Application Name:** Rent Affordability Fit Checker

**Project Option:** Predictive ML Application (Option 1 – Predictive Web Application)

### Problem Statement
Students and early-career renters often struggle to judge whether an apartment truly fits their life—not just the rent number. Typical websites apply a blunt 30% rent rule and ignore eat-out habits, neighborhood food prices, extras, roommates, and whether the area/unit is worth paying for. This application predicts a rent-fit label—**Comfortable**, **Stretch**, or **Too High**—using money basics plus lifestyle and place context, then adds decision tools most calculators lack (dual scores, reverse advice, stress tests). Results are planning guidance only, not financial advice.

### Intended Users
Students, interns, and early-career renters comparing apartments—especially people with roommates or lifestyle spending that a generic calculator misses. They enter budget and lifestyle details, see Money Fit + Place Worth, run a lifestyle stress test, get “what to change” advice, and (in the final version) save a decision journal.

### Unique Features
This is **not** a classroom demo notebook and **not** a clone of common web rent-% calculators. Unique pieces discussed with the instructor:

1. **Lifestyle-adjusted affordability assessment** — rent share + utilities + neighborhood food estimate + extras, not rent-only rules.
2. **Dual scoring system** — **Money Fit** label and a separate **Place Worth** score (neighborhood + unit condition).
3. **Lifestyle stress testing** — one-click Rarely vs Sometimes vs Often eat-out comparison for the same listing.
4. **Gap-to-Comfortable advisor** — reverse guidance (target rent share, cut eat-out/extras) instead of only scoring current inputs.
5. **Roommate share mode** — predicts on *your* portion of listed rent.
6. **Student safety-buffer warning** — flags leftover below an emergency monthly target.
7. **Decision journal** (final) — save a personal note with each prediction in SQLite.

## 2. Application Features

- **Feature 1:** Money inputs — income, listed rent, utilities, people splitting rent.
- **Feature 2:** Lifestyle inputs — eat-out level, neighborhood food cost, extras/accessories; app estimates food spend for that area.
- **Feature 3:** Place inputs — neighborhood quality and apartment condition → Place Worth score.
- **Feature 4:** Dual output — Money Fit + Place Worth, leftover, burden share, value note, safety-buffer alert.
- **Feature 5:** Gap-to-Comfortable advisor and lifestyle stress-test table.
- **Feature 6 (final):** Listing compare + SQLite decision-journal history.

**How users interact:** fill a grouped Streamlit form → click **Check rent fit** → see dual scores and metrics → review advisor tips and the eat-out stress-test table → (final) save a journal note / compare listings.

### Prototype scope vs final scope

| | November 23 prototype | December 8 final |
|---|---|---|
| Prediction | Lifestyle-aware Money Fit from saved `joblib` model | Same, polished and fully wired |
| Unique tools | Dual score + stress test + Gap-to-Comfortable advisor | Same + clearer messaging |
| Storage | Optional / light | SQLite decision journal + history |
| Compare | Not required | Side-by-side listing compare |
| Quality | Basic validation | Edge-case tests + README evidence |

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language and application logic |
| Streamlit | Web interface and form-based UI |
| Pandas | Build/clean training examples and feature tables |
| scikit-learn | Train Random Forest (or similar) rent-fit classifier |
| joblib | Save and load the trained model |
| SQLite | Store prediction history / decision journal (final) |
| Matplotlib | Optional charts of saved prediction history (final) |

## 3b. Synthetic Data Design (what we create, use, and predict)

Because real personal budget + lifestyle labels are private and hard to collect at class scale, the training set is **synthetic but rule-documented**. The model learns from generated examples that follow clear affordability rules; the app is educational, not a claim of real-world credit/rent underwriting accuracy.

### How the synthetic data is created
1. Generate about **800–1,000 rows** with a fixed random seed for reproducibility (`notebooks/train_model_starter.py`).
2. Sample realistic ranges for money variables (income, rent as a share of income, utilities, extras).
3. Sample lifestyle/place categories as scores (eat-out, neighborhood food cost, neighborhood quality, unit condition).
4. **Derive** food spend from eat-out × neighborhood food-cost bands (lookup table).
5. Compute housing cost, total monthly burden, rent-to-income, and burden-to-income.
6. Assign the target label from burden bands, with a small quality nudge (weak place + Stretch → Too High).
7. Save to `data/rent_fit_training.csv` and train/export `models/rent_fit_model.joblib`.

### Attributes put into the dataset (inputs / features)

| Attribute | Type | Example / range | Role |
|---|---|---|---|
| `income` | numeric | ~$2,200–$12,000 / mo | Ability to pay |
| `rent` / `rent_share` | numeric | ~15–50% of income (listed rent; share if roommates) | Main housing cost |
| `utilities` | numeric | ~$50–$350 / mo | Housing add-on |
| `eat_out_score` | categorical→score | 1 Rarely, 2 Sometimes, 3 Often | Lifestyle food behavior |
| `food_cost_score` | categorical→score | 1 Low, 2 Medium, 3 High | Neighborhood food prices |
| `food_spend` | derived numeric | lookup from eat-out × food-cost | Estimated monthly food |
| `lifestyle_extras` | numeric | ~$0–$400 / mo | Accessories / extras |
| `neighborhood_quality_score` | categorical→score | 1–3 | Place quality |
| `unit_condition_score` | categorical→score | 1–3 | Apartment condition |
| `housing_cost` | derived | rent share + utilities | Feature for model |
| `total_monthly_burden` | derived | housing + food + extras | Feature for model |
| `rent_to_income` | derived | housing / income | Feature for model |
| `burden_to_income` | derived | total burden / income | Core signal for label |
| `place_worth_score` | derived | quality + condition (2–6) | Dual-score support |

### What we are looking for (prediction target)
**Target column:** `fit_label`  
**Classes:** `Comfortable` | `Stretch` | `Too High`

Labeling rules used to create the target (documented for transparency):
- **Comfortable:** `burden_to_income` ≤ 0.45
- **Stretch:** 0.45 &lt; `burden_to_income` ≤ 0.60
- **Too High:** `burden_to_income` &gt; 0.60  
- Extra nudge: if label would be Stretch but place worth is very weak (quality + condition ≤ 2), label becomes **Too High**

The live app also shows **Place Worth** and leftover metrics, but the ML classifier’s main predicted class is `fit_label`.

### Missing / incomplete data: what is required to predict
The Streamlit form is designed so prediction does **not** rely on sparse scraped data. For a prediction to run:

| Field | Required? | If missing / invalid |
|---|---|---|
| Monthly income | **Required** | Block prediction; show error (must be &gt; 0) |
| Listed rent | **Required** | Block prediction; show error (cannot be negative) |
| Utilities | **Required** | Block prediction; default not assumed blank |
| Eat out | **Required** | Must pick Rarely / Sometimes / Often |
| Neighborhood food cost | **Required** | Must pick Low / Medium / High |
| Extras / accessories | **Required** (can be $0) | Blank → treat as error or coerce to 0 only if user enters 0 |
| Neighborhood quality | **Required** | Must pick Low / Medium / High |
| Unit condition | **Required** | Must pick Needs work / Average / Excellent |
| Roommates | **Required** | Default 1; reject values &lt; 1 |
| Safety buffer | Optional for model | Used for warning only; default $300 |
| Decision journal note | Optional | Not used by the model |

**Missing-data policy for training and inference**
- Training synthetic data is generated **complete** (no random NaNs by default), so the baseline model trains on full rows.
- For realism in Deliverable 2/final, I may inject a small missingness check (about **0–5%** optional fields only) and drop/impute those rows in the notebook—but **core money + lifestyle category fields stay required**.
- At prediction time, the app **does not impute** required fields behind the scenes. If anything required is missing/invalid, it returns a clear validation error instead of a silent guess.
- Derived fields (`food_spend`, ratios, burden) are always computed from the required inputs, so they are not “missing” if inputs are valid.

**Bottom line:** the model expects a complete lifestyle-aware feature vector; roughly **all core attributes above must be present** to predict. Optional journal text and safety buffer do not block the classifier.

## 4. Application Architecture

![Application architecture](docs/architecture.png)

### How the Application Works

1. The user enters money basics (including roommates), lifestyle/food choices, place ratings, and an optional journal note.
2. The Streamlit interface (`app.py`) passes the values to Python.
3. The `RentFitPredictor` class validates inputs and builds lifestyle-adjusted features (rent share, food estimate, extras, burden, place worth).
4. The application loads `models/rent_fit_model.joblib` and runs classification inference (preview rules until prototype model wiring is complete).
5. Dual scores are shown, then Gap-to-Comfortable tips and an eat-out stress-test table.
6. In the final version, predictions + journal notes are saved through `database.py`.

Training happens offline in `notebooks/` and exports the joblib file. The web app does **not** retrain on each prediction.

### Planned Python modules / classes and roles

| Component | Role |
|---|---|
| `notebooks/train_model_starter.py` (or `.ipynb`) | Create labeled data, train/evaluate model, export `joblib` |
| `rent_predictor.py` → `RentFitPredictor` | Validate inputs, engineer features, predict, advisor + stress test |
| `app.py` | Streamlit UI only (forms, results, unique tools display) |
| `database.py` | SQLite helpers for history / decision journal |
| `models/rent_fit_model.joblib` | Serialized trained model for inference |

### Preliminary interface sketch

![Preliminary interface sketch](docs/interface_sketch.png)

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
│   └── train_model_starter.py
├── data/
│   └── rent_fit_training.csv          # generated locally; not committed
└── docs/
    ├── architecture.png
    ├── interface_sketch.png
    └── DELIVERABLE1_CHECKLIST.md
```

**Important files**
- `app.py` — Streamlit UI (grouped money / lifestyle / place inputs + unique tools)
- `rent_predictor.py` — `RentFitPredictor` class (validate, features, predict, advisor, stress test)
- `database.py` — SQLite helpers for history / journal (final)
- `notebooks/train_model_starter.py` — training starter that exports the joblib model
- `docs/architecture.png` — labeled architecture / pipeline diagram
- `docs/interface_sketch.png` — preliminary interface sketch

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
- Current scaffold includes a rule-based preview so the UI and unique tools run before the joblib model is fully wired for Deliverable 2.
- No API keys or secrets are required. Do not commit `.env` files or credentials.

## 7. Testing and Validation

| Test | Expected Result | Actual Result |
|---|---|---|
| Normal inputs (income/rent/utilities + lifestyle defaults) | Dual scores + leftover + food estimate | Pending — Deliverable 2 |
| Invalid or missing input (blank / negative values) | Helpful error message | Pending — Deliverable 2 |
| High eat-out + expensive neighborhood food | Higher burden; may move Comfortable → Stretch/Too High | Pending — Deliverable 2 |
| Lifestyle stress test | Rarely / Sometimes / Often rows with different leftovers | Pending — Deliverable 2 |
| Model interaction after training | Label from saved joblib model | Pending — Deliverable 2 |
| History / journal feature | Saved note + prediction display | Pending — final |

**Known limitations (Deliverable 1):** Food spend is estimated from eat-out × neighborhood food-cost bands. Labels use documented synthetic rules. Educational guidance only—not professional financial advice.

## 8. AI-Assisted Development Disclosure / Workflow

**AI Tools Used:** ChatGPT, Cursor, GitHub Copilot

Deliverable 1 requires showing **where AI-assisted development fits into the planned workflow**. Plan below:

| Build stage | What I own | Where AI may help |
|---|---|---|
| Problem & unique features | Lifestyle-adjusted fit, dual scoring, stress testing design | Critique clarity of feature wording |
| Architecture & modules | Keep `app.py` / `RentFitPredictor` / `database.py` separated | Suggest file layout and docstrings |
| Model training | Labeling rules, feature list, evaluation checks | Help debug pandas/sklearn errors |
| Streamlit UI | Input grouping and which unique tools to show | Draft widget layout / fix Streamlit errors |
| SQLite journal | Which fields to store for history | Draft SQL helper functions |
| Testing & README | Test cases and presentation explanation | Improve README wording; suggest edge tests |

### How AI Was Used so far
For Deliverable 1, AI helped draft README structure, repository scaffold wording, and architecture/interface documentation. I selected the unique features, Option 1 design, and module boundaries.

### Student Contributions
I defined the personal rent-fit problem, chose Option 1, designed the lifestyle-adjusted / dual-score / stress-test approach, planned the architecture (`app.py` → `RentFitPredictor` → joblib → SQLite), and will own labeling rules, integration, testing, and explanation of the final code.

**Student statement:** I reviewed, tested, and can explain the code and technologies used in my application, including code developed with AI assistance. Significant AI help will remain disclosed in this README through the final submission.

## 9. Challenges and Lessons Learned

**Challenge 1:** Rent alone is not enough for a personal “can I afford this?” decision.  
**Solution (planned):** Lifestyle-adjusted burden + dual Money Fit / Place Worth scoring.

**Challenge 2:** Keeping the form usable while adding lifestyle context and unique tools.  
**Solution (planned):** Group inputs into Money / Lifestyle & food / Neighborhood & unit; put advisor + stress test in the results area.

**Challenge 3:** Feature encoding must match between notebook and app.  
**Solution (planned):** One shared feature list exported with the joblib model; validate categoricals in `RentFitPredictor`.

**Anticipated technical challenges:** joblib/SQLite path handling for instructor runs; explainable food-spend bands; edge-case validation (negative amounts, roommate &lt; 1).

New skills to develop: packaging a trained model with Streamlit, class-based feature engineering for lifestyle variables, and SQLite history for a small decision app.

## 10. Application Screenshots

Screenshots will be added for Deliverable 2 / final. For Deliverable 1, the preliminary sketch is above (`docs/interface_sketch.png`).

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

1. Wire the Streamlit app fully to the trained joblib model (replace preview rules) for Deliverable 2.
2. Add listing compare + SQLite decision-journal history for the final submission.
3. Optional presets (e.g., “student who eats out often”) to speed data entry.

---

### Implementation sequence (Deliverable 1 plan)

| Stage | Focus |
|---|---|
| Nov 16 | Proposal / README design, architecture, AI workflow, GitHub scaffold |
| Nov 17–19 | Finalize labeled data; train/export `rent_fit_model.joblib` |
| Nov 20–22 | Connect `RentFitPredictor` to saved model; polish dual-score UI |
| Nov 23 prototype | Working model-backed prediction + stress test + advisor |
| Nov 24–30 | SQLite journal/history + listing compare |
| Dec 1–7 | Validation, tests, screenshots, presentation prep |
| Dec 8 final | Complete app, README disclosure, live demonstration |

### Documentation Timeline

- **Deliverable 1 – November 16:** Complete the project overview, planned features, proposed technologies, preliminary architecture diagram, planned project structure, and AI workflow. These are planning sections and may change as development progresses.
- **Deliverable 2 – November 23:** Update the README to reflect implementation progress and initial testing.
- **Final Deliverable – December 8:** Complete all sections, verify setup instructions, add screenshots, and provide final links.
