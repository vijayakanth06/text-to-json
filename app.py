import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import groq

app = Flask(__name__)
CORS(app)

client = groq.Client(api_key="")

def generate_response(user_query):
    """Handles user queries using the Groq model."""
    
    prompt = [
        {"role": "system", "content": """You are a text-to-JSON converter specialized in analyzing multilingual inputs 
        (Tamil, English, Tanglish) and converting them into structured JSON format.

        ### Rules to Follow:
        1. **Output Only JSON** with format: {"product_name": "apple", "quantity": 500, "unit_name": "g"}
        2. Recognize **Tamil slang and number words** (arai → 0.5, kaal → 0.25, etc.)
        3. Extract **product name, quantity, and unit name**
        4. Convert **unit names to standard short forms** ("kg", "g", "mg"). Default to "g" if missing.
        5. Handle **multi-line input** and return a JSON list for multiple items.

        ### Example Input:
        ```
        thakkali 5 kg
        beetroot 3kg
        arakilo kothumai
        ```

        ### Expected Output:
        ```json
        [
          {"product_name": "thakkali", "quantity": 5, "unit_name": "kg"},
          {"product_name": "beetroot", "quantity": 3, "unit_name": "kg"},
          {"product_name": "kothumai", "quantity": 0.5, "unit_name": "kg"}
        ]
        ```"""},
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
