import streamlit as st
import pickle
import time

# Load models
scaler = pickle.load(open("scaler.pkl", "rb"))
kmeans = pickle.load(open("kmeans.pkl", "rb"))

cluster_names = {
    0: "High Earner, Low Saver",
    1: "Financially Balanced",
    2: "Struggling Saver"
}

cluster_details = {
    0: {
        "insight": "You have a high income but tend to overspend, especially on non-essential items.",
        "gaps": ["Low savings discipline", "High discretionary spending"],
        "actions": [
            "Reduce discretionary spending by at least 20%",
            "Set a fixed monthly savings goal (minimum 25% of income)"
        ]
    },
    1: {
        "insight": "You maintain a balanced financial lifestyle with controlled spending and savings.",
        "gaps": ["Scope to optimize investments", "Can increase savings rate"],
        "actions": [
            "Increase savings by 5-10% gradually",
            "Start investing in diversified assets (e.g., mutual funds)"
        ]
    },
    2: {
        "insight": "Your expenses are high relative to your income, making it difficult to save.",
        "gaps": ["Low or negative savings", "High essential expense burden"],
        "actions": [
            "Track and reduce essential expenses where possible",
            "Create a strict monthly budget plan",
            "Focus on increasing income sources if possible"
        ]
    }
}

st.title("Student Financial Persona Analyzer")

monthly_income = st.number_input("Monthly Income", min_value=0.0)
essential_spend = st.number_input("Essential Spending", min_value=0.0)
discretionary_spend = st.number_input("Discretionary Spending", min_value=0.0)

def behavior_agent(user_features, scaler, kmeans):
    user_scaled = scaler.transform(user_features)
    cluster_id = kmeans.predict(user_scaled)[0]
    return cluster_id


def gap_agent(cluster_id, cluster_details):
    return cluster_details[cluster_id]


def action_agent(details):
    return details["actions"]

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

    st.subheader("🤖 AI Agent Workflow")

    with st.spinner("Running Behavior Analysis Agent..."):
        time.sleep(1)
        cluster_id = behavior_agent(user_features, scaler, kmeans)
    st.info("✔ Behavior Analysis Completed")

    with st.spinner("Detecting Financial Gaps..."):
        time.sleep(1)
        details = gap_agent(cluster_id, cluster_details)
    st.info("✔ Gap Detection Completed")

    with st.spinner("Generating Action Plan..."):
        time.sleep(1)
        actions = action_agent(details)
    st.info("✔ Action Planning Completed")

    st.success(f"Your Financial Persona: {cluster_names[cluster_id]}")

    st.subheader("📊 Insight")
    st.write(details["insight"])

    st.subheader("⚠️ Financial Gaps")
    for gap in details["gaps"]:
        st.write(f"- {gap}")

    st.subheader("🎯 Recommended Actions")
    for action in details["actions"]:
        st.write(f"- {action}")
