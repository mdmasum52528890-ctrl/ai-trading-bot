from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from PIL import Image
import io
import json
from threading import Thread

app = Flask(__name__)
CORS(app)

genai.configure(api_key="YOUR_GEMINI_API_KEY")

def analyze_image(image_bytes):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"temperature": 0.0})
        prompt = """Analyze this trading chart. Read the exact latest time visible on the chart (e.g., "16:12:00" or "16:12"). Predict the color of the next 5 1-minute candlesticks (GREEN or RED). You must reply ONLY with a valid JSON object. Format exactly like this: {"current_time": "16:12:00", "predictions": ["GREEN", "RED", "GREEN", "RED", "GREEN"]}"""
        image = Image.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except:
        return {"current_time": "00:00:00", "predictions": ["GREEN", "RED", "GREEN", "RED", "GREEN"]}

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({"error": "No image"}), 400
    file = request.files['image']
    res = analyze_image(file.read())
    return jsonify(res)

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()
