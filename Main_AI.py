from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import json
from gtts import gTTS
import pygame
import datetime
import os

# Configure the Google Generative AI API
genai.configure(api_key='AIzaSyCs0czuASCQGrgYEOOqZHWiU-VcX6l1aEU')
model = genai.GenerativeModel('gemini-1.0-pro')

# Constants
HISTORY_FILE = 'conversation_history.json'
SPEECH_FILE = 'static/speech.mp3'  # Use static folder to serve files

# Flask app
app = Flask(__name__)

# Load conversation history from a file
def load_history(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save conversation history to a file
def save_history(filename, history):
    with open(filename, 'w') as file:
        json.dump(history, file, indent=4)

# Create a prompt from the conversation history
def create_prompt(history):
    return "".join(
        f"User: {entry['user']}\n{entry.get('ai', '')}\n"
        for entry in history
    ) + "User: "

# Get the current date and time as a string
def get_date_time():
    now = datetime.datetime.now()
    return now.strftime("ปี%Y เดือน%m วันที่%d %Hนาฬิกา %Mนาที %Sวินาที")

# Generate AI response and append to history
def generate_ai_response(prompt, user_input, history):
    response = model.generate_content(prompt + user_input)
    ai_text = response.text.strip()

    if ai_text.lower().startswith("ai:"):
        ai_text = ai_text[3:].strip()

    history.append({"user": user_input, "ai": ai_text})
    return ai_text

# Convert text to speech and save it
def text_to_speech(text, lang='th'):
    tts = gTTS(text, lang=lang, slow=False)
    tts.save(SPEECH_FILE)

# Route for the web interface
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '').strip().lower()

    history = load_history(HISTORY_FILE)

    if "วันที่เท่าไร" in user_input or "กี่โมง" in user_input:
        ai_response = get_date_time()
    else:
        prompt = create_prompt(history)
        ai_response = generate_ai_response(prompt, user_input, history)

    text_to_speech(ai_response)
    save_history(HISTORY_FILE, history)

    return jsonify({'response': ai_response, 'audio_url': f'/{SPEECH_FILE}'})

# Run the app
if __name__ == '__main__':
    # Ensure 'static' directory exists
    os.makedirs('static', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
