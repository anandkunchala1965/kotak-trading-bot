from flask import Flask, request, jsonify
import requests
import os
import json
import urllib.parse

app = Flask(__name__)

# ===== CONFIG =====
TOKEN = os.getenv("KOTAK_TOKEN")

# IMPORTANT: correct base URL
BASE_URL = "https://mis.kotaksecurities.com"

LOT_SIZE = 1  # 1 lot

# ===== PLACE ORDER FUNCTION =====
def place_order(symbol, side, price):

    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded",
        "neo-fin-key": "neotradeapi",
        "Accept": "application/json"
    }

order_data = {
    "am": "NO",
    "dq": "0",
    "es": "nse_fo",
    "mp": "0",
    "pc": "MIS",
    "pf": "N",
    "pr": str(price),
    "pt": "L",              # 🔥 FIXED
    "ot": "L",              # 🔥 ADDED
    "prc": str(price),      # 🔥 ADDED
    "qt": str(LOT_SIZE),
    "rt": "DAY",
    "tp": "0",
    "ts": symbol,
    "tt": "B" if side == "BUY" else "S"
}

    # 🔥 CRITICAL: URL ENCODE jData
    payload = urllib.parse.urlencode({
        "jData": json.dumps(order_data)
    })

    response = requests.post(url, headers=headers, data=payload)

    print("Order Response:", response.text)
    return response.text


# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json
    print("Received:", data)

    action = data.get("action")   # BUY / SELL
    symbol = data.get("symbol")   # OPTION SYMBOL
    price = data.get("price")     # LTP

    if not action or not symbol:
        return jsonify({"error": "Missing data"}), 400

    result = place_order(symbol, action, price)

    return jsonify({
        "status": "order sent",
        "response": result
    })


# ===== HEALTH CHECK =====
@app.route('/')
def home():
    return "Running"
