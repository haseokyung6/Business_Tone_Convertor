import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
client = None
if api_key:
    client = Groq(api_key=api_key)

@app.route('/api/convert', methods=['POST'])
def convert():
    if not client:
        return jsonify({"error": "GROQ_API_KEY is not configured on Vercel"}), 500

    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        original_text = data.get('text')
        target_persona = data.get('target_persona', 'boss')

        prompts = {
            "boss": "You are a professional business communication assistant. Convert the following text into a formal, concise, and respectful report format suitable for a boss. Focus on clarity and conclusions.",
            "colleague": "You are a professional business communication assistant. Convert the following text into a polite, clear, and cooperative message suitable for a teammate.",
            "customer": "You are a professional business communication assistant. Convert the following text into a highly polite, service-oriented, and professional message suitable for a customer."
        }
        
        system_prompt = prompts.get(target_persona, prompts["boss"])

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": original_text}
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7,
            max_tokens=1024,
        )
        
        converted_text = chat_completion.choices[0].message.content
        return jsonify({"converted_text": converted_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

