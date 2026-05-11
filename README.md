# travel-budget-planner
A modular Python-based application that helps travelers plan their trips by providing real-time currency conversion and AI-powered travel advice. This project was designed with a focus on Object-Oriented Programming (OOP) and clean modular architecture.

#Features
Real-Time Currency Conversion: Automatically converts your local budget (NGN) to your destination currency (USD) using live API data.
AI Travel Consultant: Integrates with Google Gemini AI to provide personalized spending tips based on your destination and budget.
Expense Tracker: A built-in tool to log your spending and see how much of your daily limit remains.
Modular Design: Built using separate modules for AI logic, budget reporting, and currency handling for easy maintenance.

Language: Python 3.x
Interface: Streamlit
AI Engine: Google Gemini API (google-generativeai)
Data: ExchangeRate-API (via requests)

# Project Structure
• app.py: The main entry point for the Streamlit UI.
• ai_advice.py: Handles communication with the Gemini AI model.
• currency_converter.py: Manages real-time exchange rate fetching.
• budget_report.py: Contains the logic for calculating daily limits and totals.
• requirements.txt: List of all necessary Python libraries.

# Setup & Run
# Clone Repo  git clone https://github.com/MOHBASH7/travel-budget-planner.git
cd travel-budget-planner

Install Dependencies  pip install -r requirements.txt

Run Application   streamlit run app.py
