

import requests
import re
import json
from datetime import datetime

class CurrencyConverter:

    def __init__(self, home_currency, destination_currency, api_key):

        self.home_currency = home_currency.upper()
        self.destination_currency = destination_currency.upper()
        self.api_key = api_key
        self.exchange_rate = None

    def validate_currency_code(self, code):
        """
        Validate currency codes like USD, NGN, GBP using regex.
        """

        pattern = r"^[A-Z]{3}$"

        if re.match(pattern, code):
            return True
        
        return False
    
    def fetch_rate(self):
        """
        Fetches live exchange rate from ExchangeRate API. 
        """

        # Validate currency codes
        if not self.validate_currency_code(self.home_currency):
            raise ValueError("Invalid home currency code.")
        
        if not self.validate_currency_code(self.destination_currency):
            raise ValueError("Invalid destination currency code.")
        
        # API URL
        url = (
            f"https://v6.exchangerate-api.com/v6/7c6b374a7db03ff604042479/latest/USD"
            f"{self.api_key}/latest/{self.home_currency}"
        )

        try:

            response = requests.get(url)

            # Raise error if request fails
            response.raise_for_status()

            data = response.json()

        except requests.exceptions.RequestException:
            raise Exception("Failed to connect to exchange rate server.")
        
        # Check API result
        if data["result"] != "success":
            raise Exception("Failed to fetch exchange rate data.")
        
        # Check if destination currency exists
        if self.destination_currency not in data["conversion_rates"]:
            raise Exception("Destination currency not found.")

        # Save exchange rate
        self.exchange_rate = data["conversion_rates"][
            self.destination_currency
        ]

        return self.exchange_rate
        
    
    def convert(self, amount):
        """
        Converts amount from home currnecy to destination currency.
        """

        # Validate amount
        try:
            amount = float(amount)

            if amount <= 0:
                raise ValueError("Amount must be greater than 0.")
        
        except ValueError:
            raise ValueError("Amount must be a positive number.")
        
        # Fetch exchange rate if not already fetched
        if self.exchange_rate is None:
            self.fetch_rate()

        if self.exchange_rate is None:
            raise Exception("Exchange rate could not be fetched.")

        converted_amount = (float(amount) * float(self.exchange_rate))

        # Save conversion in history
        self.save_conversion(amount, converted_amount)

        return converted_amount
    
    def save_conversion(self, amount, converted_amount):
        """
        Saves conversion history to JSON file.
        """

        filename = "conversion_history.json"

        conversion_record = {
            "date": str(datetime.now()),
            "from_currency": self.home_currency,
            "to_currency": self.destination_currency,
            "amount": amount,
            "converted_amount": converted_amount,
            "exchange_rate": self.exchange_rate
        }

        try: 

            # Load existing data
            try:

                with open(filename, "r") as file:
                    history = json.load(file)

            except FileNotFoundError:
                history = []

            # Add new record
            history.append(conversion_record)

            # Save updated history
            with open(filename, "w") as file:
                json.dump(history, file, indent=4)

        except Exception:
            print("Could not save conversion history.")

def main():

    print("\n===== Currency Converter =====\n")

    api_key = "7c6b374a7db03ff604042479"

    try:

        home_currency = input(
            "Enter home currency (e.g. NGN): "
        )

        destination_currency = input(
            "Enter destination currency (e.g. USD): "
        )

        amount = input(
            "Enter amount to convert: "
        )

        converter = CurrencyConverter(
            home_currency,
            destination_currency,
            api_key
        )

        rate = converter.fetch_rate()

        converted = converter.convert(amount)

        print("\n===== Conversion Result =====")
        print(f"Exchange Rate: {rate}")
        print(
            f"{amount} {home_currency.upper()} "
            f"= {converted:.2f} "
            f"{destination_currency.upper()}"
        )

    except Exception as error:
        print(f"\nError: {error}")

if __name__ == "__main__":
    main()