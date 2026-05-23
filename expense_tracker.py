import json
import csv
import os
import re
from datetime import datetime

DATA_FILE = "expenses.json"

class Expense:
    def __init__(self, description, amount, category="General", date=None):
        self.description = str(description).strip()
        self.amount = float(amount)
        self.category = str(category).strip() if category else "General"
        self.date = date or datetime.now().strftime("%Y-%m-%d")

    def validate(self):
        return bool(self.description) and self.amount > 0

    def to_dict(self):
        return {
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            description=data.get("description", ""),
            amount=data.get("amount", 0),
            category=data.get("category", "General"),
            date=data.get("date"),
        )

    @staticmethod
    def parse_amount_from_text(text):
        if not text:
            return None
        match = re.search(r"[-+]?\d{1,3}(?:[.,]\d{3})*(?:\.\d+)?|\d+\.\d+|\d+", str(text))
        if not match:
            return None
        return float(match.group(0).replace(",", ""))

class ExpenseTracker:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump([], file)

    def load_expenses(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError):
            data = []
        return [Expense.from_dict(item) for item in data]

    def save_expenses(self, expenses):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump([expense.to_dict() for expense in expenses], file, indent=4)

    def add_expense(self, expense):
        if not isinstance(expense, Expense):
            raise TypeError("Expense must be an Expense instance.")
        if not expense.validate():
            raise ValueError("Expense must contain a description and positive amount.")
        expenses = self.load_expenses()
        expenses.append(expense)
        self.save_expenses(expenses)
        return expense

    def total_spent(self):
        return sum(exp.amount for exp in self.load_expenses())

    def export_json(self, filename=None):
        filename = filename or f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as file:
            json.dump([expense.to_dict() for expense in self.load_expenses()], file, indent=4)
        return filename

    def export_csv(self, filename=None):
        filename = filename or f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["date", "category", "description", "amount"])
            for expense in self.load_expenses():
                writer.writerow([expense.date, expense.category, expense.description, f"{expense.amount:.2f}"])
        return filename
