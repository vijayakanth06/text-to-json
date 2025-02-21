import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import groq

app = Flask(__name__)
CORS(app)

client = groq.Client(api_key="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")

def generate_response(user_query):
    """Handles user queries using the Groq model."""
    
    prompt = [
        {"role": "system", "content": """you are a text-to-JSON converter. Analyze the given text and 
        convert it into JSON format. Do not provide any output other than JSON. The JSON should contain 
        three parameters: {"product_name":"apple","quantity":500,"unit_name":"g"}.
        Identify unit names correctly, store values as they are, and convert tanglish words into numbers 
        (e.g., "arai" → 0.5, "kaal" → 0.25). Use short forms for units (e.g., "kg" for kilogram)."""},
        {"role": "user", "content": f"User Query: {user_query}"}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=prompt
    )

    raw_response = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_response)  # Convert string JSON to a Python dictionary
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format received"}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json.get("text")  # Get user input from request
    if not data:
        return jsonify({"error": "I couldn't find relevant information. Can you rephrase?"})

    reply = generate_response(data)  # Get structured response from model
    return jsonify(reply)  # Return JSON response directly

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
