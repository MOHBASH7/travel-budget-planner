import json
from datetime import datetime
import requests
import streamlit as st
import os

DATA_FILE = "budget_history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_data(new_entry):
    data = load_data()
    data.append(new_entry)
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


st.title("Trip Budget Planner")
st.write("Hello! If you see this, the integration is working.")
if st.button("Clear History"):
    if os.path.exists("budget_history.json"):
        os.remove("budget_history.json")


budget = st.number_input("Enter your total budget (₦)", min_value=0.0)
expense_name = st.text_input("Expense Name (e.g., Hotel, Food)")
amount = st.number_input("Amount", min_value=0.0)

st.sidebar.header("Settings")
target_currency = st.sidebar.selectbox("Convert to:", ["USD", "EUR", "GBP"])


# Load previous history
history = load_data()

st.title("Currency Converter & Tracker")

# User inputs
amount = st.number_input("Amount (₦)", min_value=0.0)
target = st.selectbox("Convert to", ["USD", "EUR", "GBP"])

if st.button("Convert and Save"):
    # Imagine 'converted_val' comes from your API logic
    converted_val = amount * 0.00065 # Example rate
    
    entry = {
        "original_naira": amount,
        "converted_val": converted_val,
        "currency": target
    }
    
    save_data(entry)
    st.success(f"Saved! {amount} ₦ is approx {converted_val:.2f} {target}")

# Display history
if history:
    st.subheader("Recent Conversions")
    st.table(history)

class TripBudget:
    def __init__(self, destination, duration_days, total_budget, currency):
        self.destination = destination
        self.duration_days = duration_days
        self.total_budget = total_budget
        self.currency = currency

    def daily_limit(self):
        if self.duration_days <= 0:
            return 0
        return round(self.total_budget / self.duration_days, 2)

    def save_to_file(self, filename):
        data = {
            "destination": self.destination,
            "duration_days": self.duration_days,
            "total_budget": self.total_budget,
            "currency": self.currency
        }
        try:
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
            print(f"Data saved to {filename}")
        except IOError as e:
            print(f"File Error: {e}")

    def check_public_holidays(self, country_code, year):
        url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching holidays: {e}")
            return []
