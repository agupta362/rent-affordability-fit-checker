"""Streamlit prototype for Rent Affordability Fit Checker (Deliverable 2).

Core interaction: form inputs -> RentFitPredictor -> joblib model inference
Integrations: trained ML model + optional SQLite decision journal save
"""

from pathlib import Path

import streamlit as st

from database import list_predictions, save_prediction
from rent_predictor import MODEL_PATH, RentFitPredictor

st.set_page_config(page_title="Rent Fit Checker", page_icon="🏠", layout="centered")

st.title("Rent Affordability Fit Checker")
st.caption("CIS 3400 Project 2 · Deliverable 2 prototype · Option 1 Predictive Web App")

predictor = RentFitPredictor()
model_ready = predictor.load_model()

if model_ready:
    st.success("Integration ready: trained `rent_fit_model.joblib` loaded for inference.")
else:
    st.warning(
        "Model file not found. Run `python notebooks/train_model_starter.py` then refresh. "
        f"Expected path: `{MODEL_PATH}`"
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
- **Decision journal** — optional note saved with SQLite history
        """
    )

st.subheader("Money basics")
c1, c2, c3, c4 = st.columns(4)
with c1:
    income = st.number_input("Monthly income ($)", min_value=0.0, value=4500.0, step=100.0)
with c2:
    rent = st.number_input("Listed rent ($)", min_value=0.0, value=1800.0, step=50.0)
with c3:
    utilities = st.number_input("Utilities ($)", min_value=0.0, value=150.0, step=10.0)
with c4:
    roommates = st.number_input("People splitting rent", min_value=1, value=1, step=1)

st.subheader("Lifestyle & food")
l1, l2, l3 = st.columns(3)
with l1:
    eat_out = st.selectbox("Do you eat out?", ["Rarely", "Sometimes", "Often"], index=1)
with l2:
    neighborhood_food_cost = st.selectbox(
        "Neighborhood food cost",
        ["Low", "Medium", "High"],
        index=1,
        help="How expensive restaurants/groceries feel in that area",
    )
with l3:
    lifestyle_extras = st.number_input(
        "Extras / accessories ($/mo)",
        min_value=0.0,
        value=100.0,
        step=25.0,
    )

st.subheader("Neighborhood & unit")
n1, n2, n3 = st.columns(3)
with n1:
    neighborhood_quality = st.selectbox(
        "Neighborhood quality",
        ["Low", "Medium", "High"],
        index=1,
    )
with n2:
    unit_condition = st.selectbox(
        "Apartment / rent condition",
        ["Needs work", "Average", "Excellent"],
        index=1,
    )
with n3:
    safety_buffer = st.number_input(
        "Safety buffer ($/mo)",
        min_value=0.0,
        value=300.0,
        step=50.0,
        help="Student emergency leftover target",
    )

decision_note = st.text_input(
    "Decision journal note (optional)",
    placeholder="e.g. Close to campus, noisy street, likes the kitchen...",
)
save_to_history = st.checkbox("Save this check to SQLite history", value=True)

run = st.button("Check rent fit", type="primary")

if run:
    try:
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
st.subheader("Recent SQLite history")
history = list_predictions(limit=8)
if history:
    st.dataframe(history, use_container_width=True)
else:
    st.caption("No saved checks yet. Run a prediction with history saving enabled.")

st.caption(
    f"Model path: `{Path(MODEL_PATH).as_posix()}` · "
    "Remaining for final: listing compare polish, more tests, screenshots, presentation."
)
