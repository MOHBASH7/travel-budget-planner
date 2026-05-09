import json
from datetime import datetime
import requests


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
