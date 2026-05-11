import streamlit as st
import requests
import re
import json
import pandas as pd
from ai_advice import AIAdvisor

# ---------------- CONFIG & OOP ----------------
st.set_page_config(page_title="Travel Budget Planner", layout="wide")
advisor = AIAdvisor()

class Validator:
    """Using Regular Expressions to validate inputs"""
    @staticmethod
    def is_valid_currency(code):
        # Regex: Exactly 3 uppercase letters
        return bool(re.fullmatch(r"^[A-Z]{3}$", code.upper()))

# ---------------- UI ----------------
st.title("🌍 Travel Budget Planner")

# Sidebar for Exports (File Handling Requirement)
with st.sidebar:
    st.header("💾 Export Data")
    if st.button("Export Budget to JSON"):
        data = {"expenses": st.session_state.get("expenses", []), "total": sum(e['cost'] for e in st.session_state.get("expenses", []))}
        with open("budget_report.json", "w") as f:
            json.dump(data, f)
        st.success("Saved to budget_report.json")

# ---------------- INPUTS ----------------
col1, col2, col3 = st.columns(3)
with col1:
    home_curr = st.text_input("Home Currency", "NGN").upper()
    dest_curr = st.text_input("Destination Currency", "USD").upper()
with col2:
    dest_name = st.text_input("Destination City/Country")
    total_amount = st.number_input("Total Amount to Convert", min_value=0.0)
with col3:
    trip_days = st.number_input("Duration (Days)", min_value=1)

# ---------------- LOGIC ----------------
if st.button("🚀 Calculate & Get AI Advice"):
    # 1. Validation (Regex & Exception Handling)
    if not Validator.is_valid_currency(home_curr) or not Validator.is_valid_currency(dest_curr):
        st.error("Invalid Currency Code! Please use 3 letters (e.g., USD).")
    else:
        try:
            # 2. API Call (Currency)
            url = f"https://open.er-api.com/v6/latest/{home_curr}"
            response = requests.get(url)
            response.raise_for_status() # Check for bad request
            data = response.json()
            
            if dest_curr not in data["rates"]:
                raise ValueError("Destination currency not found in exchange data.")

            rate = data["rates"][dest_curr]
            converted_total = total_amount * rate
            daily = converted_total / trip_days

            # 3. Display Results
            st.divider()
            c1, c2 = st.columns(2)
            c1.metric(f"Total in {dest_curr}", f"{converted_total:,.2f}")
            c2.metric("Daily Limit", f"{daily:,.2f}")

            # 4. AI Advice
            with st.spinner("AI is thinking..."):
                advice = advisor.generate_advice(dest_name, converted_total, trip_days, dest_curr)
                st.info(advice)

        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- EXPENSE TRACKER ----------------
st.divider()
st.header("💸 Expense Tracker")
if "expenses" not in st.session_state: st.session_state.expenses = []

ec1, ec2 = st.columns([2, 1])
with ec1:
    item = st.text_input("What did you buy?")
with ec2:
    cost = st.number_input("Cost", min_value=0.0, key="exp_cost")

if st.button("Add Expense"):
    if item:
        st.session_state.expenses.append({"item": item, "cost": cost})

if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    st.table(df)
    st.write(f"**Total Spent:** {df['cost'].sum():,.2f}")
