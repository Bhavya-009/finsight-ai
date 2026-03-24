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

total_expense = essential_spend + discretionary_spend
savings = max(0, monthly_income - total_expense)
savings_ratio = (monthly_income - total_expense) / (monthly_income + 1e-6)
discretionary_pct = discretionary_spend / (monthly_income + 1e-6)
essential_pct = essential_spend / (monthly_income + 1e-6)

user_features = [[
        monthly_income,
        savings_ratio,
        discretionary_pct,
        essential_pct
    ]]

def behavior_agent(user_features, scaler, kmeans):
    user_scaled = scaler.transform(user_features)
    cluster_id = kmeans.predict(user_scaled)[0]
    return cluster_id

def insight_agent(savings_ratio, essential_pct, discretionary_pct):
    
    # Strong positive case
    if savings_ratio > 0.3 and discretionary_pct < 0.25:
        return "You are managing your finances very well with a strong savings habit and controlled spending."

    # Good but can improve
    elif savings_ratio > 0.2:
        return "Your financial situation is stable, but there is room to further optimize savings and spending."

    # High essential burden
    elif essential_pct > 0.6:
        return "A significant portion of your income is spent on essentials, which limits your ability to save."

    # High discretionary issue
    elif discretionary_pct > 0.3:
        return "High spending on non-essential items is impacting your ability to save effectively."

    # Low savings case
    else:
        return "Your current spending pattern is limiting your savings potential, and requires immediate attention."

def gap_agent(cluster_id, cluster_details, essential_pct, discretionary_pct, savings_ratio):
    base = cluster_details[cluster_id].copy()

    dynamic_gaps = []

    if savings_ratio <= 0.2:
        dynamic_gaps.append("Low savings rate")

    if essential_pct >= 0.4:
        dynamic_gaps.append("High essential expenses")

    if discretionary_pct >= 0.3:
        dynamic_gaps.append("High discretionary spending")

    # If nothing triggered - fallback
    if not dynamic_gaps:
        dynamic_gaps.append("Moderate financial balance, but scope for optimization")

    base["gaps"] = dynamic_gaps

    return base

def action_agent(details, income, essential_spend, discretionary_spend):
    actions = []
    monthly_target_savings = 0

    for gap in details["gaps"]:
        
        # Saving 25% more
        if "Low savings rate" in gap:
            target_savings = int(0.25 * income)
            actions.append(f"Increase savings to at least ₹{target_savings} per month")
            monthly_target_savings += target_savings

        # Reducing 10% essential expense more
        if "High essential expenses" in gap:
            reduce_amt = int(0.1 * essential_spend)
            actions.append(f"Try reducing essential expenses by ₹{reduce_amt}/month")
            monthly_target_savings += reduce_amt

        # Reducing 20% High expense
        if "High discretionary spending" in gap:
            reduce_amt = int(0.2 * discretionary_spend)
            actions.append(f"Reduce discretionary spending by ₹{reduce_amt}/month")
            monthly_target_savings += reduce_amt

        # for moderate finance ratios
        if "Moderate financial balance, but scope for optimization" in gap:
            actions.append("Optimize budget allocation to improve savings")

    return actions, monthly_target_savings

def calculate_health_score(income, expenses, savings):
    # -- try for some better approach --
    if income == 0:
        return 0

    savings_ratio = savings / income
    expense_ratio = expenses / income
    savings_score = 0
    expense_score = 0

    # Savings contribution (max 50)
    savings_score += min(savings_ratio * 100, 50)
    # Expense penalty (max 50)
    expense_score += max(0, (1 - expense_ratio)) * 50

    total_score = savings_score + expense_score

    return round(savings_score), round(expense_score), round(total_score)

def generate_explanation(savings_ratio, essential_pct, discretionary_pct):
    if savings_ratio < 0.2:
        return "Your savings are low and need immediate attention."

    elif discretionary_pct > 0.3:
        return "High discretionary spending is reducing your ability to save."
    
    elif essential_pct > 0.4:
        return "A large portion of your income is going into essential expenses, limiting savings."

    elif savings_ratio > 0.3:
        return "You are maintaining a strong savings habit. Keep it up!"

    else:
        return "Your finances are stable but can be optimized further."

if st.button("Analyze"):
    s_score, e_score, score = calculate_health_score(
        monthly_income, total_expense, savings
    )
    
    # AI Agent Working -
    st.subheader("🤖 AI Agent Workflow")

    with st.spinner("Running Behavior Analysis Agent..."):
        time.sleep(1)
        cluster_id = behavior_agent(user_features, scaler, kmeans)
    st.info("✔ Behavior Analysis Completed")

    with st.spinner("Detecting Financial Gaps..."):
        time.sleep(1)
        details = gap_agent(
            cluster_id, 
            cluster_details, 
            essential_pct, 
            discretionary_pct, 
            savings_ratio)
    st.info("✔ Gap Detection Completed")

    with st.spinner("Generating Action Plan..."):
        time.sleep(1)
        actions, monthly_target_savings = action_agent(
            details, 
            monthly_income, 
            essential_spend, 
            discretionary_spend)
    st.info("✔ Action Planning Completed")

    # -- FINAL OUTPUT --

    st.success(f"Your Financial Persona: {cluster_names[cluster_id]}")
    
    st.divider()

    st.subheader("📊 Financial Health Overview")
    st.metric("Financial Health Score", f"{score}/100")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("💰 Savings Score", f"{s_score}/50")

    with col2:
        st.metric("📉 Expense Score", f"{e_score}/50")

    st.write(generate_explanation(savings_ratio, essential_pct, discretionary_pct))

    st.divider()

    st.subheader("📊 Insight")
    insight = insight_agent(savings_ratio, essential_pct, discretionary_pct)
    st.write(insight)

    st.divider()

    st.subheader("⚠️ Financial Gaps")
    for gap in details["gaps"]:
        st.write(f"- {gap}")

    st.divider()

    st.subheader("🎯 Recommended Actions")
    for action in actions:
        st.write(f"- {action}")

    st.divider()
    
    st.subheader("💰 Potential Financial Impact")
    st.write(f"Your savings rate: {savings_ratio * 100 :.2f}%")
    if savings_ratio < 0.3:
        st.success(
            f"You can potentially save ₹{monthly_target_savings}/month → ₹{monthly_target_savings * 12}/year by following recommended actions"
        )
    else:
        st.info("Your savings rate is healthy. Keep maintaining this level 👍")

