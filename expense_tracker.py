from datetime import datetime

import sqlite3

def connect_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    return conn, cursor

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

filename = f"expenses_{timestamp}.csv"

def init_db():
    conn, cursor = connect_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY,
        description TEXT,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)
    conn.commit()
    conn.close()

class Expense:

    def __init__(self, description, amount, category):
        self.description = description
        self.amount = amount
        self.category = category
        self.date = datetime.now().strftime("%Y-%m-%d")

    def validate(self):
        return self.amount > 0

    def save(self):
        conn, cursor = connect_db()
        cursor.execute("""
        INSERT INTO expenses(description, amount, category, date)
        VALUES(?,?,?,?)
        """, (
            self.description,
            self.amount,
            self.category,
            self.date
        ))
        conn.commit()
        conn.close()

    def to_dict(self):
        return {
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "date": self.date
        }

class ExpenseTracker:

    def __init__(self):
        init_db()

    def add_expense(self, description, amount, category="General"):
        expense = Expense(description, amount, category)
        if not expense.validate():
            raise ValueError("Amount must be positive")
        expense.save()

    def get_total(self):
        conn, cursor = connect_db()
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total = cursor.fetchone()[0]
        conn.close()
        return total if total is not None else 0

if __name__ == "__main__":
    tracker = ExpenseTracker()
    tracker.add_expense("Food", 50, "Food")
    print(f"Current total: {tracker.get_total()}")