import streamlit as st
import pickle
import time

if "screen" not in st.session_state:
    st.session_state.screen = "home"  # default screen


# -------------------------
# NAVIGATION FUNCTION
# -------------------------
def go_to(screen_name):
    st.session_state.screen = screen_name

# -------------------------
# SCREEN 1: ENTRY (HOME)
# -------------------------
if st.session_state.screen == "home":
    st.title("Understand & Improve Your Financial Life")

    st.write("Get quick insights into your finances in seconds.")

    st.button("Start Quick Analysis ⚡", on_click=go_to, args=("quick",))
    st.button("Deep Analysis ⚡", on_click=go_to, args=("deep",))


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


if st.session_state.screen == "quick":
    st.title("Financial Persona Analyzer")
    monthly_income = st.number_input("Monthly Income", min_value=0.0)
    essential_spend = st.number_input("Essential Spending", min_value=0.0)
    discretionary_spend = st.number_input("Discretionary Spending", min_value=0.0)

    st.session_state.monthly_income = monthly_income
    st.session_state.essential_spend = essential_spend
    st.session_state.discretionary_spend = discretionary_spend

    total_expense = essential_spend + discretionary_spend

    savings = max(0, monthly_income - total_expense)
    st.session_state.savings = savings

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

        # st.success(f"Your Financial Persona: {cluster_names[cluster_id]}")

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

        st.button("Get InDepth Analysis: ", on_click=go_to, args=("deep",))
        st.button("⬅ Back", on_click=go_to, args=("home",))
    
elif st.session_state.screen == "deep":


    st.title("🔍 Deep Financial Health Analysis")
    income = st.session_state.get("monthly_income", None)
    essential = st.session_state.get("essential_spend", None)
    discretionary = st.session_state.get("discretionary_spend", None)

    if income is None:

        st.info("Let's quickly understand your basic finances first 👇")

        monthly_income = st.number_input("Monthly Income", min_value=0.0)
        essential_spend = st.number_input("Essential Spending", min_value=0.0)
        discretionary_spend = st.number_input("Discretionary Spending", min_value=0.0)

        total_expense = essential_spend + discretionary_spend
        savings = monthly_income - total_expense

        st.session_state.monthly_income = income
        st.session_state.essential_spend = essential_spend
        st.session_state.discretionary_spend = discretionary_spend
        st.session_state.total_expense = total_expense
        st.session_state.savings = savings
        st.rerun()

        st.subheader("📥 Additional Financial Details")
        emi = st.number_input("Monthly EMI (Debt)", min_value=0.0)
        investments = st.number_input("Total Investments (₹)", min_value=0.0)
        insurance = st.selectbox("Do you have insurance?", ["No", "Yes"])
        tax_saving = st.number_input("Tax-saving Investments (₹/year)", min_value=0.0)
        age = st.number_input("Your Age", min_value=16, max_value=70, value=25)

        def calculate_six_dimensions(income, expenses, savings, emi, investments, insurance, tax_saving, age):
            # 1. Emergency Preparedness 
            if expenses > 0:
                emergency = min((savings / expenses) * 100, 100)
            else:
                emergency = 100

            # 2. Insurance Coverage 
            insurance_score = 80 if insurance == "Yes" else 30

            # 3. Investment Diversification 
            if income > 0:
                invest_ratio = investments / (income * 12 + 1e-6)
                investment = min(invest_ratio * 100, 100)
            else:
                investment = 0

            # 4. Debt Health
            if income > 0:
                debt_ratio = emi / income
                debt = max(0, (1 - debt_ratio)) * 100
            else:
                debt = 0

            # 5. Tax Efficiency
            if income > 0:
                tax = min((tax_saving / (income * 12 + 1e-6)) * 100, 100)
            else:
                tax = 0

            # 6. Retirement Readiness
            savings_ratio = savings / (income + 1e-6)
            age_factor = max(0.5, (60 - age) / 40)
            retirement = min(savings_ratio * 100 * age_factor, 100)

            return (
                round(emergency),
                round(insurance_score),
                round(investment),
                round(debt),
                round(tax),
                round(retirement)
            )
        
        em, ins, inv, debt, tax, ret = calculate_six_dimensions(
            monthly_income,
            total_expense,
            savings,
            emi,
            investments,
            insurance,
            tax_saving,
            age
        )

        st.subheader("📊 Your Financial Health Breakdown")

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            st.metric("🛡️ Emergency", f"{em}/100")

        with col2:
            st.metric("🧾 Insurance", f"{ins}/100")

        with col3:
            st.metric("📊 Investment", f"{inv}/100")

        with col4:
            st.metric("💳 Debt Health", f"{debt}/100")

        with col5:
            st.metric("🧮 Tax Efficiency", f"{tax}/100")

        with col6:
            st.metric("🏖️ Retirement", f"{ret}/100")

        st.divider()

        overall_score = round((em + ins + inv + debt + tax + ret) / 6) 
        st.success(f"🌟 Overall Financial Health Score: {overall_score}/100")

        st.button("Get FIRE Plan: ")
        st.button("⬅ Back", on_click=go_to, args=("quick",))
