"""Streamlit UI for Rent Affordability Fit Checker.

Prototype target (Nov 23): money + lifestyle/neighborhood inputs -> fit label.
"""

import streamlit as st

from rent_predictor import RentFitPredictor

st.set_page_config(page_title="Rent Fit Checker", page_icon="🏠", layout="centered")

st.title("Rent Affordability Fit Checker")
st.caption("CIS 3400 Project 2 · Option 1 · Predict Comfortable / Stretch / Too High")

st.info(
    "Deliverable 1 scaffold: form + rule-based preview. "
    "Trained joblib model will replace the preview for the Nov 23 prototype."
)

st.subheader("Money basics")
c1, c2, c3 = st.columns(3)
with c1:
    income = st.number_input("Monthly income ($)", min_value=0.0, value=4500.0, step=100.0)
with c2:
    rent = st.number_input("Monthly rent ($)", min_value=0.0, value=1800.0, step=50.0)
with c3:
    utilities = st.number_input("Utilities ($)", min_value=0.0, value=150.0, step=10.0)

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
        help="Shopping, subscriptions, personal extras",
    )

st.subheader("Neighborhood & unit")
n1, n2 = st.columns(2)
with n1:
    neighborhood_quality = st.selectbox(
        "Neighborhood quality",
        ["Low", "Medium", "High"],
        index=1,
        help="Safety, transit, vibe, amenities",
    )
with n2:
    unit_condition = st.selectbox(
        "Apartment / rent condition",
        ["Needs work", "Average", "Excellent"],
        index=1,
    )

if st.button("Check rent fit", type="primary"):
    predictor = RentFitPredictor()
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
        )
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.subheader(f"Fit: {result['fit_label']}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Est. leftover", f"${result['leftover']:,.0f}")
        m2.metric("Housing share", f"{result['housing_share'] * 100:.0f}%")
        m3.metric("Total burden share", f"{result['burden_share'] * 100:.0f}%")
        st.write(f"Estimated food spend in this neighborhood: **${result['food_spend']:,.0f}/mo**")
        st.write(result["value_note"])
        if not result["model_backed"]:
            st.caption("Preview rules only — ML model coming in Deliverable 2.")

st.divider()
st.markdown("**Coming next:** saved model inference · listing compare · prediction history")
