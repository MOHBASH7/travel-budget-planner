from google import genai

client = genai.Client(api_key="AIzaSyBgJPwFvigrnLzis2qLFGQ--XWObqG9ON0")

def generate_advice(destination, budget, days):

    try:
        prompt = f"""
        You are a travel assistant.

        Destination: {destination}
        Budget: {budget}
        Days: {days}

        Give:
        - daily spending plan
        - saving tips
        - transport advice
        - food suggestions
        """

        response = client.models.generate_content(
            model="gemini-pro-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"AI Error: {e}"