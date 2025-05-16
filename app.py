from flask import Flask, request, render_template, send_from_directory
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
    try:
        return json.loads(response.text.strip("```json\n").strip("```"))
    except json.JSONDecodeError as e:
        print("JSON Error in parse_preferences:", e, "Response:", response.text)
        raise

def get_attractions(destination, interests):
    """Use Gemini SDK to generate a list of attractions based on interests."""
    interest = interests[0] if interests else "tourist attractions"
    prompt = f"""
    List 3 {interest} in {destination} as a JSON array of objects with 'name' and 'description' fields.
    Example: [{"name": "Louvre Museum", "description": "World-famous art museum"}]
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text.strip("```json\n").strip("```"))
    except json.JSONDecodeError as e:
        print("JSON Error in get_attractions:", e, "Response:", response.text)
        raise

def generate_itinerary(preferences, attractions):
    """Generate a simple itinerary using Gemini SDK."""
    attractions_json = json.dumps(attractions)  # Serialize attractions to JSON string
    prompt = f"""
    Create a {preferences['days']}-day itinerary for {preferences['destination']} with a budget of ${preferences['budget']}.
    Include activities related to {', '.join(preferences['interests'])} and these attractions: {attractions_json}.
    Output as a JSON list of daily plans with fields: day, activities (list of strings).
    Example: [{"day": 1, "activities": ["Visit Louvre", "Dinner at Le Bistro"]}, ...]
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text.strip("```json\n").strip("```"))
    except json.JSONDecodeError as e:
        print("JSON Error in generate_itinerary:", e, "Response:", response.text)
        raise

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        print("POST request received:", user_input)
        try:
            preferences = parse_preferences(user_input)
            print("Preferences:", preferences)
            attractions = get_attractions(preferences["destination"], preferences["interests"])
            print("Attractions:", attractions)
            itinerary = generate_itinerary(preferences, attractions)
            print("Itinerary:", itinerary)
            return render_template("result.html", itinerary=itinerary, destination=preferences["destination"])
        except Exception as e:
            print("Error:", str(e))
            return render_template("index.html", error=str(e))
    return render_template("index.html", error=None)

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "static"), "favicon.ico")

if __name__ == "__main__":
    app.run(debug=True)