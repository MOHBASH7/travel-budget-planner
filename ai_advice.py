import os
import random

try:
    import google.generativeai as genai
    HAVE_AI = True
except ImportError:
    HAVE_AI = False

API_KEY = os.getenv("GOOGLE_API_KEY")

if HAVE_AI and API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception:
        HAVE_AI = False
else:
    HAVE_AI = False

class AIAdvisor:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.model_name = model_name
        self.use_ai = HAVE_AI

    def generate_advice(self, destination, budget, days, currency):
        if not destination or budget <= 0 or days <= 0:
            return "Provide a destination, budget, and duration to generate advice."

        prompt = (
            f"Give a short travel budget plan for {days} days in {destination}. "
            f"Total budget: {budget:.2f} {currency}."
        )

        if self.use_ai:
            try:
                model = genai.GenerativeModel(self.model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                return self._fallback_advice(destination, budget, days, currency)

        return self._fallback_advice(destination, budget, days, currency)

    def _fallback_advice(self, destination, budget, days, currency):
        daily = budget / days if days else 0
        suggestions = [
            "Balance your spend by saving on accommodation and using local transport.",
            "Set a daily amount for food, sightseeing, and small emergencies.",
            "Divide the budget into essentials, experiences, and a safety buffer.",
        ]
        card = random.choice(suggestions)
        return (
            f"Travel advice for {destination}: With {budget:.2f} {currency} over {days} days, aim for about {daily:.2f} {currency} per day. "
            f"{card}"
        )
