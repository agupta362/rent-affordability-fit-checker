"""Final Streamlit app: Rent Affordability Fit Checker (Deliverable 3).

Core flow: form inputs -> RentFitPredictor -> joblib model inference
Integrations: trained ML model + SQLite decision journal / history
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from database import history_summary, list_predictions, save_prediction
from rent_predictor import MODEL_PATH, RentFitPredictor

st.set_page_config(page_title="Rent Fit Checker", page_icon="🏠", layout="centered")

PRESETS = {
    "Custom": None,
    "Student (budget, rarely eats out)": {
        "income": 2800.0,
        "rent": 1400.0,
        "utilities": 120.0,
        "roommates": 2,
        "eat_out": "Rarely",
        "neighborhood_food_cost": "Medium",
        "lifestyle_extras": 50.0,
        "neighborhood_quality": "Medium",
        "unit_condition": "Average",
        "safety_buffer": 250.0,
    },
    "Intern (eats out often, expensive area)": {
        "income": 4500.0,
        "rent": 2200.0,
        "utilities": 160.0,
        "roommates": 1,
        "eat_out": "Often",
        "neighborhood_food_cost": "High",
        "lifestyle_extras": 200.0,
        "neighborhood_quality": "High",
        "unit_condition": "Excellent",
        "safety_buffer": 300.0,
    },
}

st.title("Rent Affordability Fit Checker")
st.caption("CIS 3400 Project 2 · Final app · Option 1 Predictive Web Application")

predictor = RentFitPredictor()
model_ready = predictor.load_model()

if model_ready:
    st.success("Trained model loaded: `rent_fit_model.joblib` ready for inference.")
else:
    st.warning(
        "Model file not found. Run `python notebooks/train_model_starter.py` then refresh. "
        f"Expected: `{MODEL_PATH}`"
    )

with st.expander("What makes this different from typical rent calculators?", expanded=False):
    st.markdown(
        """
- **Lifestyle-adjusted fit** — eat-out, neighborhood food prices, extras
- **Dual score** — Money Fit label **and** Place Worth score
- **Gap-to-Comfortable advisor** — reverse suggestions
- **Lifestyle stress test** — Rarely vs Often eat-out impact
- **Roommate share mode** — predicts on *your* share of rent
- **Student safety buffer** — leftover emergency warning
- **Decision journal + history filters** — SQLite saved checks with search/chart
- **Listing compare** — two apartments, same lifestyle
        """
    )

preset_name = st.selectbox("Quick lifestyle preset", list(PRESETS.keys()))
preset = PRESETS[preset_name]
if preset and st.session_state.get("_applied_preset") != preset_name:
    for key, value in preset.items():
        st.session_state[key] = value
    st.session_state["_applied_preset"] = preset_name

st.subheader("Money basics")
c1, c2, c3, c4 = st.columns(4)
with c1:
    income = st.number_input(
        "Monthly income ($)",
        min_value=0.0,
        value=float(st.session_state.get("income", 4500.0)),
        step=100.0,
        key="income",
    )
with c2:
    rent = st.number_input(
        "Listed rent ($)",
        min_value=0.0,
        value=float(st.session_state.get("rent", 1800.0)),
        step=50.0,
        key="rent",
    )
with c3:
    utilities = st.number_input(
        "Utilities ($)",
        min_value=0.0,
        value=float(st.session_state.get("utilities", 150.0)),
        step=10.0,
        key="utilities",
    )
with c4:
    roommates = st.number_input(
        "People splitting rent",
        min_value=1,
        value=int(st.session_state.get("roommates", 1)),
        step=1,
        key="roommates",
    )

st.subheader("Lifestyle & food")
l1, l2, l3 = st.columns(3)
eat_options = ["Rarely", "Sometimes", "Often"]
food_options = ["Low", "Medium", "High"]
with l1:
    eat_default = st.session_state.get("eat_out", "Sometimes")
    eat_out = st.selectbox(
        "Do you eat out?",
        eat_options,
        index=eat_options.index(eat_default) if eat_default in eat_options else 1,
        key="eat_out",
    )
with l2:
    food_default = st.session_state.get("neighborhood_food_cost", "Medium")
    neighborhood_food_cost = st.selectbox(
        "Neighborhood food cost",
        food_options,
        index=food_options.index(food_default) if food_default in food_options else 1,
        key="neighborhood_food_cost",
        help="How expensive restaurants/groceries feel in that area",
    )
with l3:
    lifestyle_extras = st.number_input(
        "Extras / accessories ($/mo)",
        min_value=0.0,
        value=float(st.session_state.get("lifestyle_extras", 100.0)),
        step=25.0,
        key="lifestyle_extras",
    )

st.subheader("Neighborhood & unit")
n1, n2, n3 = st.columns(3)
qual_options = ["Low", "Medium", "High"]
cond_options = ["Needs work", "Average", "Excellent"]
with n1:
    qual_default = st.session_state.get("neighborhood_quality", "Medium")
    neighborhood_quality = st.selectbox(
        "Neighborhood quality",
        qual_options,
        index=qual_options.index(qual_default) if qual_default in qual_options else 1,
        key="neighborhood_quality",
    )
with n2:
    cond_default = st.session_state.get("unit_condition", "Average")
    unit_condition = st.selectbox(
        "Apartment / rent condition",
        cond_options,
        index=cond_options.index(cond_default) if cond_default in cond_options else 1,
        key="unit_condition",
    )
with n3:
    safety_buffer = st.number_input(
        "Safety buffer ($/mo)",
        min_value=0.0,
        value=float(st.session_state.get("safety_buffer", 300.0)),
        step=50.0,
        key="safety_buffer",
        help="Student emergency leftover target",
    )

decision_note = st.text_input(
    "Decision journal note (optional)",
    placeholder="e.g. Close to campus, noisy street, likes the kitchen...",
)
save_to_history = st.checkbox("Save this check to SQLite history", value=True)

# Soft warnings for unusual but allowed edge cases
if income > 0 and rent / max(int(roommates), 1) > income:
    st.warning("Your rent share is higher than your monthly income — expect a Too High result.")
if int(roommates) >= 5:
    st.info("Large roommate count: make sure everyone is truly splitting the listed rent.")

run = st.button("Check rent fit", type="primary")

if run:
    try:
        if income <= 0:
            raise ValueError("Monthly income must be positive.")
        if rent < 0 or utilities < 0 or lifestyle_extras < 0:
            raise ValueError("Rent, utilities, and extras cannot be negative.")
        if int(roommates) < 1:
            raise ValueError("People splitting rent must be at least 1.")

        result = predictor.predict(
            income=income,
            rent=rent,
            utilities=utilities,
            eat_out=eat_out,
            neighborhood_food_cost=neighborhood_food_cost,
            lifestyle_extras=lifestyle_extras,
            neighborhood_quality=neighborhood_quality,
            unit_condition=unit_condition,
            roommates=int(roommates),
            safety_buffer=safety_buffer,
        )
        gap = predictor.gap_to_comfortable(
            income,
            rent,
            utilities,
            eat_out,
            neighborhood_food_cost,
            lifestyle_extras,
            neighborhood_quality,
            unit_condition,
            int(roommates),
        )
        stress = predictor.lifestyle_stress_test(
            income,
            rent,
            utilities,
            neighborhood_food_cost,
            lifestyle_extras,
            neighborhood_quality,
            unit_condition,
            int(roommates),
        )
        if save_to_history:
            save_prediction(
                {
                    "income": income,
                    "rent": rent,
                    "utilities": utilities,
                    "roommates": int(roommates),
                    "eat_out": eat_out,
                    "neighborhood_food_cost": neighborhood_food_cost,
                    "lifestyle_extras": lifestyle_extras,
                    "neighborhood_quality": neighborhood_quality,
                    "unit_condition": unit_condition,
                    "food_spend": result["food_spend"],
                    "fit_label": result["fit_label"],
                    "place_worth_score": result["place_worth_score"],
                    "leftover": result["leftover"],
                    "housing_share": result["housing_share"],
                    "burden_share": result["burden_share"],
                    "decision_note": decision_note or None,
                }
            )
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.session_state["last_result"] = result
        st.session_state["last_gap"] = gap
        st.session_state["last_stress"] = stress
        st.session_state["last_note"] = decision_note

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    gap = st.session_state["last_gap"]
    stress = st.session_state["last_stress"]

    st.subheader("Dual score result")
    a, b = st.columns(2)
    a.metric("Money Fit", result["fit_label"])
    b.metric("Place Worth", f"{result['place_worth_score']}/6 · {result['place_worth_label']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Your rent share", f"${result['rent_share']:,.0f}")
    m2.metric("Est. leftover", f"${result['leftover']:,.0f}")
    m3.metric("Food in this area", f"${result['food_spend']:,.0f}")
    m4.metric("Total burden", f"{result['burden_share'] * 100:.0f}%")

    if result.get("probabilities"):
        st.caption(
            "Model class probabilities: "
            + ", ".join(f"{k}={v:.0%}" for k, v in result["probabilities"].items())
        )

    st.write(result["value_note"])
    if result["buffer_warning"]:
        st.warning(result["buffer_warning"])
    if st.session_state.get("last_note"):
        st.caption(f"Journal note: {st.session_state['last_note']}")

    if result["model_backed"]:
        st.success("Prediction from trained Random Forest model (joblib integration).")
    else:
        st.caption("Fallback rule preview — train/export the model to enable ML inference.")

    st.subheader("Gap-to-Comfortable advisor")
    if gap["already_comfortable"]:
        st.success(gap["message"])
    else:
        st.write(gap["message"])
        for tip in gap["suggestions"]:
            st.markdown(f"- {tip}")

    st.subheader("Lifestyle stress test (eat-out)")
    st.caption("Same apartment & income — only eat-out level changes.")
    st.dataframe(stress, use_container_width=True)

st.divider()
st.subheader("Compare two listings")
st.caption("Same income/lifestyle — only rent, utilities, and place ratings change.")
cmp_on = st.checkbox("Enable listing compare", value=False)
if cmp_on:
    left, right = st.columns(2)
    with left:
        st.markdown("**Listing A** (current form rent/place)")
        st.write(f"Rent ${rent:,.0f} · Utils ${utilities:,.0f}")
        st.write(f"{neighborhood_quality} area · {unit_condition}")
    with right:
        st.markdown("**Listing B**")
        rent_b = st.number_input("Listing B rent ($)", min_value=0.0, value=max(rent - 200, 0.0), step=50.0)
        util_b = st.number_input("Listing B utilities ($)", min_value=0.0, value=utilities, step=10.0)
        qual_b = st.selectbox("Listing B neighborhood", ["Low", "Medium", "High"], index=1, key="qual_b")
        cond_b = st.selectbox(
            "Listing B condition",
            ["Needs work", "Average", "Excellent"],
            index=1,
            key="cond_b",
        )
    if st.button("Compare listings"):
        try:
            res_a = predictor.predict(
                income,
                rent,
                utilities,
                eat_out,
                neighborhood_food_cost,
                lifestyle_extras,
                neighborhood_quality,
                unit_condition,
                int(roommates),
                safety_buffer,
            )
            res_b = predictor.predict(
                income,
                rent_b,
                util_b,
                eat_out,
                neighborhood_food_cost,
                lifestyle_extras,
                qual_b,
                cond_b,
                int(roommates),
                safety_buffer,
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            ca, cb = st.columns(2)
            with ca:
                st.metric("A Money Fit", res_a["fit_label"])
                st.write(f"Leftover ${res_a['leftover']:,.0f}")
                st.write(f"Place Worth {res_a['place_worth_score']}/6")
            with cb:
                st.metric("B Money Fit", res_b["fit_label"])
                st.write(f"Leftover ${res_b['leftover']:,.0f}")
                st.write(f"Place Worth {res_b['place_worth_score']}/6")
            if res_b["leftover"] > res_a["leftover"]:
                st.info("Listing B leaves more monthly leftover under the same lifestyle.")
            elif res_a["leftover"] > res_b["leftover"]:
                st.info("Listing A leaves more monthly leftover under the same lifestyle.")
            else:
                st.info("Both listings leave about the same leftover under the same lifestyle.")

st.divider()
st.subheader("SQLite history, filters, and trend")
hf1, hf2, hf3 = st.columns(3)
with hf1:
    label_filter = st.selectbox("Filter by Money Fit", ["All", "Comfortable", "Stretch", "Too High"])
with hf2:
    note_search = st.text_input("Search journal notes", placeholder="campus, kitchen...")
with hf3:
    hist_limit = st.slider("Rows to show", min_value=5, max_value=50, value=15)

history = list_predictions(limit=hist_limit, fit_label=label_filter, search_note=note_search or None)
summary = history_summary()
st.caption(f"Saved checks in database: **{summary['total']}** · counts by label: {summary['by_label'] or '{}'}")

if history:
    hist_df = pd.DataFrame(history)
    st.dataframe(hist_df, use_container_width=True)
    trend = hist_df.sort_values("id")[["id", "leftover", "burden_share", "fit_label"]]
    st.line_chart(trend.set_index("id")[["leftover"]])
    st.caption("Trend chart: leftover ($) for recent saved checks (filtered view).")
else:
    st.caption("No saved checks match these filters yet.")

st.caption(f"Model path: `{Path(MODEL_PATH).as_posix()}` · Final Deliverable 3")
