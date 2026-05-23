import json
import requests
from datetime import datetime, date, timedelta

class TripBudget:
    HOLIDAY_API_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"

    def __init__(
        self,
        destination,
        duration_days,
        total_budget,
        currency,
        start_date=None,
        end_date=None,
        country_code=None,
    ):
        self.destination = str(destination).strip()
        self.duration_days = int(duration_days)
        self.total_budget = float(total_budget)
        self.currency = str(currency).strip().upper()
        self.start_date = self._parse_date(start_date)
        self.end_date = self._parse_date(end_date)
        self.country_code = str(country_code).strip().upper() if country_code else None

        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date.")

    def _parse_date(self, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value:
            return datetime.strptime(value, "%Y-%m-%d").date()
        raise ValueError("Date must be a datetime.date or YYYY-MM-DD string.")

    def daily_limit(self):
        if self.duration_days <= 0:
            return 0
        return round(self.total_budget / self.duration_days, 2)

    def total_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return self.duration_days

    def to_dict(self):
        return {
            "destination": self.destination,
            "duration_days": self.duration_days,
            "total_budget": self.total_budget,
            "currency": self.currency,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "country_code": self.country_code,
        }

    def save_to_file(self, filename):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=4)
        return filename

    def compare_with(self, other):
        if not isinstance(other, TripBudget):
            raise TypeError("Can only compare TripBudget instances.")

        difference = round(self.total_budget - other.total_budget, 2)
        return {
            "first_destination": self.destination,
            "second_destination": other.destination,
            "difference": abs(difference),
            "higher_budget": self.destination if difference > 0 else other.destination if difference < 0 else "equal",
        }

    def _fetch_holidays_for_year(self, year):
        if not self.country_code:
            return []

        url = self.HOLIDAY_API_URL.format(year=year, country_code=self.country_code)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return data
        except requests.RequestException:
            pass
        return []

    def holidays_in_range(self):
        if not self.country_code or not self.start_date or not self.end_date:
            return []

        holidays = []
        year = self.start_date.year
        while year <= self.end_date.year:
            for entry in self._fetch_holidays_for_year(year):
                try:
                    holiday_date = datetime.fromisoformat(entry.get("date")).date()
                except (TypeError, ValueError):
                    continue
                if self.start_date <= holiday_date <= self.end_date:
                    holidays.append(
                        {
                            "date": entry.get("date"),
                            "localName": entry.get("localName"),
                            "name": entry.get("name"),
                        }
                    )
            year += 1

        return holidays
