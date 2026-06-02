import json
import re
from datetime import date

import requests
import streamlit as st

from ai_advice import AIAdvisor
from budget_report import BudgetReport
from currency_converter import CurrencyConverter
from expense_tracker import Expense, ExpenseTracker
from trip_budget import TripBudget

st.set_page_config(page_title="Travel Budget Planner", layout="wide")
advisor = AIAdvisor()

class Validator:
    @staticmethod
    def is_valid_currency(code):
        return bool(re.fullmatch(r"[A-Z]{3}", str(code).strip().upper()))

    @staticmethod
    def is_valid_country_code(code):
        return bool(re.fullmatch(r"[A-Z]{2}", str(code).strip().upper()))

    @staticmethod
    def extract_price(text):
        if not text:
            return None
        match = re.search(r"[-+]?\d{1,3}(?:[.,]\d{3})*(?:\.\d+)?|\d+\.\d+|\d+", str(text))
        if not match:
            return None
        return float(match.group(0).replace(",", ""))


def load_expense_tracker():
    if "expense_tracker" not in st.session_state:
        st.session_state.expense_tracker = ExpenseTracker()
    return st.session_state.expense_tracker


def format_money(value):
    return f"{value:,.2f}"


st.title("🌍 Travel Budget Planner")
st.write("Plan your travel costs, track expenses, compare destinations, and export reports.")

with st.sidebar:
    st.header("💾 Export Files")
    if st.button("Export Trip Report"):
        trip = st.session_state.get("current_trip")
        if not trip:
            st.error("Compute a trip first before exporting the report.")
        else:
            expenses = load_expense_tracker().load_expenses()
            report = BudgetReport(trip, expenses)
            result = report.export_json()
            st.success(result)
    if st.button("Export Expense JSON"):
        filename = load_expense_tracker().export_json()
        st.success(f"Saved expense file: {filename}")
    if st.button("Export Expense CSV"):
        filename = load_expense_tracker().export_csv()
        st.success(f"Saved expense file: {filename}")

# Trip Planner
st.header("✈️ Trip Budget Calculator")
col1, col2, col3 = st.columns(3)
with col1:
    home_currency = st.text_input("Home Currency", "NGN").upper()
    destination_currency = st.text_input("Destination Currency", "USD").upper()
    destination_country = st.text_input("Destination Country Code", "US").upper()
with col2:
    destination_name = st.text_input("Destination Name", "New York")
    raw_amount = st.text_input("Amount to Convert", "1000")
with col3:
    trip_days = st.number_input("Duration (Days)", min_value=1, value=7)
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())

if st.button("🚀 Calculate Travel Budget"):
    try:
        if not Validator.is_valid_currency(home_currency) or not Validator.is_valid_currency(destination_currency):
            raise ValueError("Please enter valid 3-letter currency codes.")

        if not Validator.is_valid_country_code(destination_country):
            raise ValueError("Please enter a valid 2-letter destination country code.")

        amount = Validator.extract_price(raw_amount)
        if amount is None:
            amount = float(raw_amount)

        converter = CurrencyConverter(home_currency, destination_currency)
        converted_amount = converter.convert(amount)
        trip = TripBudget(
            destination=destination_name or destination_currency,
            duration_days=trip_days,
            total_budget=converted_amount,
            currency=destination_currency,
            start_date=start_date,
            end_date=end_date,
            country_code=destination_country,
        )
        st.session_state.current_trip = trip

        daily_limit = trip.daily_limit()
        st.metric(f"Total in {destination_currency}", format_money(converted_amount))
        st.metric("Recommended Daily Limit", format_money(daily_limit))

        holidays = trip.holidays_in_range()
        if holidays:
            st.warning("Your trip overlaps with public holidays in the destination country.")
            st.table(holidays)
        else:
            st.info("No public holidays found on your selected travel dates.")

        with st.spinner("Generating travel advice..."):
            advice = advisor.generate_advice(destination_name, converted_amount, trip_days, destination_currency)
            st.info(advice)

    except ValueError as exc:
        st.error(f"Input or exchange API error: {exc}")
    except ConnectionError as exc:
        st.error(f"Currency API connection error: {exc}")
    except requests.RequestException as exc:
        st.error(f"Network error: {exc}")
    except Exception as exc:
        st.error(f"Unexpected error: {exc}")

# Destination comparison
st.write("---")
st.header("🧭 Compare Two Travel Destinations")
compare_cols = st.columns(2)
with compare_cols[0]:
    compare_dest1 = st.text_input("Destination 1 Currency", "EUR").upper()
    compare_name1 = st.text_input("Destination 1 Name", "Paris")
    compare_amount1 = st.text_input("Destination 1 Budget", "1000")
    compare_days1 = st.number_input("Destination 1 Days", min_value=1, value=5, key="days1")
with compare_cols[1]:
    compare_dest2 = st.text_input("Destination 2 Currency", "GBP").upper()
    compare_name2 = st.text_input("Destination 2 Name", "London")
    compare_amount2 = st.text_input("Destination 2 Budget", "1000")
    compare_days2 = st.number_input("Destination 2 Days", min_value=1, value=5, key="days2")

if st.button("Compare Destinations"):
    try:
        if not Validator.is_valid_currency(home_currency):
            raise ValueError("Please enter a valid home currency before comparing destinations.")
        if not Validator.is_valid_currency(compare_dest1) or not Validator.is_valid_currency(compare_dest2):
            raise ValueError("Please enter valid 3-letter currency codes for both destinations.")

        amount1 = Validator.extract_price(compare_amount1)
        amount2 = Validator.extract_price(compare_amount2)
        if amount1 is None:
            amount1 = float(compare_amount1)
        if amount2 is None:
            amount2 = float(compare_amount2)

        converter1 = CurrencyConverter(home_currency, compare_dest1)
        converter2 = CurrencyConverter(home_currency, compare_dest2)

        converted1 = converter1.convert(amount1)
        converted2 = converter2.convert(amount2)

        trip1 = TripBudget(compare_name1 or compare_dest1, compare_days1, converted1, compare_dest1)
        trip2 = TripBudget(compare_name2 or compare_dest2, compare_days2, converted2, compare_dest2)

        comparison = trip1.compare_with(trip2)

        c1, c2, c3 = st.columns(3)
        c1.metric(f"{compare_name1} Total", format_money(converted1))
        c2.metric(f"{compare_name2} Total", format_money(converted2))
        c3.metric("Budget Difference", format_money(comparison["difference"]))

        st.success(
            f"{comparison['higher_budget']} has the larger total budget based on your inputs."
            if comparison["difference"] > 0
            else "Both trip budgets are equal."
        )

    except ValueError as exc:
        st.error(f"Input error: {exc}")
    except requests.RequestException as exc:
        st.error(f"Network error: {exc}")
    except Exception as exc:
        st.error(f"Error: {exc}")

# Expense tracking
st.write("---")
st.header("💸 Expense Tracker")
tracker = load_expense_tracker()
expense_col1, expense_col2 = st.columns([2, 1])
with expense_col1:
    expense_description = st.text_input("Expense Description", "Lunch at airport")
    expense_category = st.text_input("Category", "Food")
    raw_expense_amount = st.text_input("Amount or sentence with price", "12.50")
with expense_col2:
    expense_amount = st.number_input("Numeric Amount", min_value=0.0, value=0.0)

if st.button("Add Expense"):
    try:
        amount = expense_amount if expense_amount > 0 else Validator.extract_price(raw_expense_amount)
        if amount is None or amount <= 0:
            raise ValueError("Please enter a valid expense amount.")
        if not expense_description:
            raise ValueError("Please add a description for the expense.")

        expense = Expense(expense_description, amount, expense_category or "General")
        tracker.add_expense(expense)
        st.success("Expense added.")
    except ValueError as exc:
        st.error(f"Expense error: {exc}")
    except Exception as exc:
        st.error(f"Error: {exc}")

expenses = tracker.load_expenses()
if expenses:
    st.table([expense.to_dict() for expense in expenses])
    st.write(f"**Total Spent:** {format_money(tracker.total_spent())}")
else:
    st.info("No expenses recorded yet.")

# Export summary
st.write("---")
st.header("🗂️ Export Summary")
if st.button("Save current trip to JSON"):
    trip = st.session_state.get("current_trip")
    if not trip:
        st.error("There is no current trip to export. Please run a calculation first.")
    else:
        filename = trip.save_to_file(f"trip_budget_{trip.destination}_{date.today().isoformat()}.json")
        st.success(f"Trip saved to {filename}")

if st.button("Save expenses to CSV"):
    filename = tracker.export_csv()
    st.success(f"Expenses exported to {filename}")

if st.button("Save expenses to JSON"):
    filename = tracker.export_json()
    st.success(f"Expenses exported to {filename}")