import streamlit as st
import pickle

# Load models
scaler = pickle.load(open("scaler.pkl", "rb"))
kmeans = pickle.load(open("kmeans.pkl", "rb"))

cluster_names = {
    0: "High-Income Overextended",
    1: "Balanced Planner",
    2: "Financially Constrained"
}

st.title("Student Financial Persona Analyzer")

monthly_income = st.number_input("Monthly Income", min_value=0.0)
essential_spend = st.number_input("Essential Spending", min_value=0.0)
discretionary_spend = st.number_input("Discretionary Spending", min_value=0.0)

if st.button("Analyze"):

    total_expense = essential_spend + discretionary_spend
    savings_ratio = (monthly_income - total_expense) / (monthly_income + 1e-6)
    discretionary_pct = discretionary_spend / (monthly_income + 1e-6)
    essential_pct = essential_spend / (monthly_income + 1e-6)

    user_features = [[
        monthly_income,
        savings_ratio,
        discretionary_pct,
        essential_pct
    ]]

    user_scaled = scaler.transform(user_features)
    cluster_id = kmeans.predict(user_scaled)[0]

    st.success(f"Your Financial Persona: {cluster_names[cluster_id]}")
