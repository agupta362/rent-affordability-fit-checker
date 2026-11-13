"""Streamlit UI for Rent Affordability Fit Checker.

Prototype target (Nov 23): 3 inputs -> fit label + leftover.
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

col1, col2, col3 = st.columns(3)
with col1:
    income = st.number_input("Monthly income ($)", min_value=0.0, value=4500.0, step=100.0)
with col2:
    rent = st.number_input("Monthly rent ($)", min_value=0.0, value=1800.0, step=50.0)
with col3:
    utilities = st.number_input("Utilities ($)", min_value=0.0, value=150.0, step=10.0)

if st.button("Check rent fit", type="primary"):
    predictor = RentFitPredictor()
    try:
        result = predictor.predict(income, rent, utilities)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.subheader(f"Fit: {result['fit_label']}")
        st.write(f"Estimated leftover: **${result['leftover']:,.2f}**")
        st.write(f"Housing share of income: **{result['housing_share'] * 100:.1f}%**")
        if not result["model_backed"]:
            st.caption("Preview rules only — ML model coming in Deliverable 2.")

st.divider()
st.markdown("**Coming next:** saved model inference · listing compare · prediction history")
