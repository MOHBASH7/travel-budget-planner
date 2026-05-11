import google.generativeai as genai

# Replace with your actual Gemini API Key
API_KEY = "AIzaSyCtzO-V4UGFO24N0-waW88mB_vsnswnSdY"
genai.configure(api_key=API_KEY)

class AIAdvisor:
    def __init__(self):
        # Using 1.5-flash as it often has more stable quota for free tier
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_advice(self, destination, budget, days, currency):
        if not destination or budget <= 0:
            return "Missing destination or budget."
        
        try:
            prompt = (
                f"Give a short travel budget plan for {days} days in {destination}. "
                f"Total budget: {budget:.2f} {currency}."
            )
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Friendly handling of the 429 "Quota" error
            if "429" in str(e):
                return "⚠️ The AI is on a break! You've hit the free limit. Please wait 60 seconds and try again."
            return f"AI Error: {str(e)}"
