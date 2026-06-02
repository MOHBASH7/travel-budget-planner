import requests
import re
import json
from datetime import datetime

class CurrencyConverter:
    """Convert amounts between two three-letter currency codes."""

    API_KEY = "698a0e024264d791fb590b78"
    API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{{}}"
    HISTORY_FILE = "conversion_history.json"

    def __init__(self, home_currency, destination_currency):
        self.home_currency = str(home_currency).strip().upper()
        self.destination_currency = str(destination_currency).strip().upper()
        self.exchange_rate = None

    def validate_currency_code(self, code):
        return bool(re.fullmatch(r"[A-Z]{3}", str(code).strip().upper()))

    def fetch_rate(self):
        if not self.validate_currency_code(self.home_currency):
            raise ValueError(f"Invalid home currency code '{self.home_currency}'.")
        if not self.validate_currency_code(self.destination_currency):
            raise ValueError(f"Invalid destination currency code '{self.destination_currency}'.")

        try:
            response = requests.get(self.API_URL.format(self.home_currency), timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as error:
            raise ConnectionError(f"Exchange rate request failed: {error}")
        except ValueError as error:
            raise ValueError(f"Invalid response from exchange rate service: {error}")

        if data.get("result") != "success" or "conversion_rates" not in data:
            error_type = data.get("error-type") or data.get("error") or "unknown error"
            debug_info = json.dumps(data, indent=2, ensure_ascii=False)
            raise ValueError(
                f"Exchange rate service error: {error_type}. Response: {debug_info}"
            )

        if self.destination_currency not in data["conversion_rates"]:
            raise ValueError(f"Destination currency {self.destination_currency} not available.")

        self.exchange_rate = data["conversion_rates"][self.destination_currency]
        return self.exchange_rate

    def convert(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Invalid amount. Please provide a number.")

        if amount < 0:
            raise ValueError("Amount must be zero or positive.")

        if self.exchange_rate is None:
            self.fetch_rate()

        if self.exchange_rate is None:
            raise RuntimeError("Exchange rate could not be loaded.")

        converted_amount = amount * self.exchange_rate
        self.save_conversion(amount, converted_amount)
        return converted_amount

    def save_conversion(self, amount, converted_amount):
        record = {
            "date": datetime.now().isoformat(),
            "from_currency": self.home_currency,
            "to_currency": self.destination_currency,
            "amount": amount,
            "converted_amount": converted_amount,
            "exchange_rate": self.exchange_rate,
        }

        try:
            history = []
            try:
                with open(self.HISTORY_FILE, "r", encoding="utf-8") as file:
                    history = json.load(file)
            except FileNotFoundError:
                history = []

            history.append(record)
            with open(self.HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump(history, file, indent=4)
        except (OSError, ValueError):
            pass


def main():
    print("\n===== Currency Converter =====\n")

    try:
        home_currency = input("Enter home currency (e.g. NGN): ")
        destination_currency = input("Enter destination currency (e.g. USD): ")
        amount = input("Enter amount to convert: ")

        converter = CurrencyConverter(home_currency, destination_currency)
        converted = converter.convert(amount)

        print("\n===== Conversion Result =====")
        print(f"Exchange Rate: {converter.exchange_rate}")
        print(
            f"{amount} {home_currency.upper()} = {converted:.2f} {destination_currency.upper()}"
        )
    except Exception as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()
