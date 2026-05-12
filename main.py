from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from threading import Thread

app = Flask(__name__)
CORS(app)

def get_ai_prediction(pair):
    tickers = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "JPY=X"}
    symbol = tickers.get(pair, "EURUSD=X")
    
    try:
        data = yf.download(symbol, period="2d", interval="1m", progress=False)
        if len(data) < 20: return "WAIT", 0
        
        df = data[['Open', 'High', 'Low', 'Close']].copy()
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        train_data = df.iloc[:-1]
        X = train_data[['Open', 'High', 'Low', 'Close']]
        y = train_data['Target']
        
        model = RandomForestClassifier(n_estimators=50)
        model.fit(X, y)
        
        last_candle = df.iloc[[-1]][['Open', 'High', 'Low', 'Close']]
        prediction = model.predict(last_candle)[0]
        prob = model.predict_proba(last_candle).max() * 100
        
        res = "CALL" if prediction == 1 else "PUT"
        return res, round(prob, 2)
    except Exception as e:
        return "ERROR", 0

@app.route('/')
def home():
    return "BOT IS RUNNING PERFECTLY!"

@app.route('/api/signal')
def get_signal():
    pair = request.args.get('pair', 'EURUSD')
    direction, accuracy = get_ai_prediction(pair)
    return jsonify({"direction": direction, "probability": accuracy})

def run():
    app.run(host='0.0.0.0', port=8080)

t = Thread(target=run)
t.start()
