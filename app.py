import streamlit as st
import requests
import re
import json
from ai_advice import AIAdvisor

# 1. OOP Requirement: Initialize the AI class
advisor = AIAdvisor()

st.title("✈️ Simple Travel Planner")

# --- INPUT SECTION ---
# We use simple inputs so you can easily point to them during defense
home_curr = st.text_input("Home Currency (e.g. NGN)", "NGN")
dest_curr = st.text_input("Destination Currency (e.g. USD)", "USD")
destination = st.text_input("Destination Name")
amount = st.number_input("Budget Amount", min_value=0.0)
days = st.number_input("Days", min_value=1)

# --- MAIN LOGIC ---
if st.button("Calculate & Get AI Advice"):
    
    # 2. REGEX Requirement: Validate currency is exactly 3 letters
    if not re.fullmatch(r"^[A-Z]{3}$", home_curr.upper()):
        st.error("Invalid Home Currency format!")
    
    else:
        try:
            # 3. EXCEPTION HANDLING: Try to get exchange rates
            url = f"https://open.er-api.com/v6/latest/{home_curr}"
            data = requests.get(url).json()
            
            rate = data["rates"][dest_curr.upper()]
            converted = amount * rate
            
            # Show basic results
            st.write(f"### Total Budget: {converted:.2f} {dest_curr}")
            
            # 4. AI Requirement: Call the AI Advisor class
            with st.spinner("AI is thinking..."):
                advice = advisor.generate_advice(destination, converted, days, dest_curr)
                st.info(advice)
                
        except Exception as e:
            st.error("Could not fetch data. Check your connection or currency codes.")

# --- FILE HANDLING SECTION ---
st.header("💾 Save Data")
if st.button("Export to JSON"):
    # 5. FILE HANDLING Requirement: Save a local file
    sample_data = {"dest": destination, "budget": amount}
    with open("budget.json", "w") as f:
        json.dump(sample_data, f)
    st.success("Saved to budget.json!")
