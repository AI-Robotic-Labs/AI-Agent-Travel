from flask import Flask, request, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # Use Gemini 1.5 Flash for cost-efficiency

def parse_preferences(user_input):
    """Use Gemini SDK to parse user input into structured preferences."""
    prompt = f"""
    Extract travel preferences from the following input in JSON format:
    Input: "{user_input}"
    Output format: {{ "destination": "", "budget": 0, "days": 0, "interests": [] }}
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.strip("```json\n").strip("```"))

def get_attractions(destination, interests):
    """Use Gemini SDK to generate a list of attractions based on interests."""
    interest = interests[0] if interests else "tourist attractions"
    prompt = f"""
    List 3 {interest} in {destination} as a JSON array of objects with 'name' and 'description' fields.
    Example: [{"name": "Louvre Museum", "description": "World-famous art museum"}]
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.strip("```json\n").strip("```"))

def generate_itinerary(preferences, attractions):
    """Generate a simple itinerary using Gemini SDK."""
    prompt = f"""
    Create a {preferences['days']}-day itinerary for {preferences['destination']} with a budget of ${preferences['budget']}.
    Include activities related to {', '.join(preferences['interests'])} and these attractions: {attractions}.
    Output as a JSON list of daily plans with fields: day, activities (list of strings).
    Example: [{"day": 1, "activities": ["Visit Louvre", "Dinner at Le Bistro"]}, ...]
    """
    response = model.generate_content(prompt)
    return json.loads(response.text.strip("```json\n").strip("```"))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        try:
            # Parse preferences
            preferences = parse_preferences(user_input)
            # Fetch attractions using Gemini
            attractions = get_attractions(preferences["destination"], preferences["interests"])
            # Generate itinerary
            itinerary = generate_itinerary(preferences, attractions)
            return render_template("result.html", itinerary=itinerary, destination=preferences["destination"])
        except Exception as e:
            return render_template("index.html", error=str(e))
    return render_template("index.html", error=None)

if __name__ == "__main__":
    app.run(debug=True)