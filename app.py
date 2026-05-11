import streamlit as st
import requests
from ai_advice import generate_advice

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Travel Budget Planner",
    page_icon="✈️",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# ---------------- HEADER ----------------
st.markdown("""
# 🌍 Travel Budget Planner
### Plan smarter. Spend better. Travel stress-free.
""")

st.markdown("---")

# ---------------- INPUT SECTION ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💱 Currency Setup")
    home_currency = st.text_input("Home Currency (e.g. NGN)")
    destination_currency = st.text_input("Destination Currency (e.g. USD)")

with col2:
    st.markdown("### ✈️ Trip Details")
    destination = st.text_input("Destination")
    amount = st.number_input("Amount", min_value=0.0)

with col3:
    st.markdown("### 📅 Duration")
    days = st.number_input("Travel Days", min_value=1)

st.markdown("---")

# ---------------- BUTTON ----------------
if st.button("🚀 Generate Travel Budget", use_container_width=True):

    try:
        # -------- CURRENCY CONVERSION --------
        url = f"https://open.er-api.com/v6/latest/{home_currency}"
        data = requests.get(url).json()

        rate = data["rates"][destination_currency]
        converted = amount * rate
        daily_budget = converted / days

        st.success("Budget calculated successfully")

        # ---------------- RESULTS ----------------
        colA, colB = st.columns(2)

        with colA:
            st.metric("💰 Total Budget", f"{converted:.2f}")

        with colB:
            st.metric("📉 Daily Budget", f"{daily_budget:.2f}")

        # ---------------- AI ADVICE ----------------
        st.markdown("## 🤖 AI Travel Advice")

        advice = generate_advice(destination, converted, days)
        st.info(advice)

    except Exception as e:
        st.error("Something went wrong while generating budget.")
        st.write(e)

# ---------------- EXPENSE TRACKER ----------------
st.markdown("---")
st.markdown("## 💸 Expense Tracker")

with st.expander("➕ Add Expense"):
    item = st.text_input("Expense Name")
    cost = st.number_input("Cost", min_value=0.0)

    if st.button("Add Expense"):
        if item and cost > 0:
            st.session_state.expenses.append((item, cost))
            st.success("Expense added!")

if st.session_state.expenses:
    st.markdown("### 📋 Your Expenses")

    total = 0
    for i, c in st.session_state.expenses:
        st.write(f"• {i} - {c}")
        total += c

    st.warning(f"Total Spent: {total}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("🌍 Travel Budget Planner | Built with Streamlit")