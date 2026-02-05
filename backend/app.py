import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Flask with frontend folder as static source
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Initialize Groq client
# Ensure you have set GROQ_API_KEY in your .env file
api_key = os.getenv("GROQ_API_KEY")
client = None

if api_key:
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
else:
    print("Warning: GROQ_API_KEY not found in environment variables.")

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "BizTone Converter API"})

@app.route('/api/convert', methods=['POST'])
def convert_text():
    data = request.json
    
    if not data or 'text' not in data or 'target_persona' not in data:
        return jsonify({"error": "Missing 'text' or 'target_persona' in request"}), 400
    
    original_text = data['text']
    target_persona = data['target_persona']
    
    if not client:
        return jsonify({"error": "Server configuration error: AI service unavailable"}), 503

    # Define system prompts based on persona
    prompts = {
        "boss": "You are a professional business communication assistant. Convert the following text into a formal, concise, and respectful report format suitable for a boss. Focus on clarity and conclusions.",
        "colleague": "You are a professional business communication assistant. Convert the following text into a polite, clear, and cooperative message suitable for a teammate. Be respectful but less formal than for a boss.",
        "customer": "You are a professional business communication assistant. Convert the following text into a highly polite, service-oriented, and professional message suitable for a customer. Use honorifics and emphasize service mindset."
    }
    
    system_prompt = prompts.get(target_persona, prompts["boss"])
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": original_text
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct", # Using a fast, efficient model available on Groq
            temperature=0.7,
            max_tokens=1024,
        )
        
        converted_text = chat_completion.choices[0].message.content
        return jsonify({"converted_text": converted_text})

    except Exception as e:
        error_msg = str(e)
        print(f"API Error: {error_msg}")
        return jsonify({"error": f"Failed to process request: {error_msg}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
