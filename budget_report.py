import json
import csv
import os
from datetime import datetime

class BudgetReport:
    def __init__(self, trip_budget_obj, expenses_list):
        self.trip = trip_budget_obj
        self.expenses = expenses_list
        # [span_6](start_span)Requirement: Handle file timestamps[span_6](end_span)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def total_spent(self):
        # Refinement: Handle empty lists gracefully
        if not self.expenses:
            return 0
        return sum(expense.amount for expense in self.expenses)

    def remaining_budget(self):
        return self.trip.total_budget - self.total_spent()

    def export_json(self):
        filename = f"report_{self.timestamp}.json"
       
        # [span_7](start_span)[span_8](start_span)Requirement: Export data to JSON[span_7](end_span)[span_8](end_span)
        data = {
            "trip_info": {
                "destination": self.trip.destination,
                "budget": self.trip.total_budget
            },
            "summary": {
                "spent": self.total_spent(),
                "remaining": self.remaining_budget()
            },
            "expenses": [e.to_dict() for e in self.expenses]
        }
       
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            return f"Success: {filename}"
        except IOError:
            return "Error: Could not write to file."

    def export_csv(self):
        filename = f"expenses_{self.timestamp}.csv"
       
        # [span_9](start_span)[span_10](start_span)Requirement: Export to CSV[span_9](end_span)[span_10](end_span)
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Category", "Description", "Amount"])
                for e in self.expenses:
                    # Refinement: Ensure amount is treated as a number
                    writer.writerow([e.date, e.category, e.description, f"{e.amount:.2f}"])
            return f"Success: {filename}"
        except Exception as e:
            return f"Error: {e}"