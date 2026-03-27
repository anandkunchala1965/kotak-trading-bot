from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# ===== CONFIG =====
TOKEN = os.getenv("KOTAK_TOKEN")
BASE_URL = "https://api.kotaksecurities.com"  # will adjust if needed

LOT_SIZE = 1  # 1 lot only

# ===== PLACE ORDER FUNCTION =====
def place_order(symbol, side, price):

    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded",
        "neo-fin-key": "neotradeapi"
    }

    order_data = {
        "am": "NO",
        "dq": "0",
        "es": "nse_fo",              # OPTIONS
        "mp": "0",
        "pc": "MIS",
        "pf": "N",
        "pr": "0",
        "pt": "L",                  # LIMIT ORDER (IMPORTANT)
        "qt": str(LOT_SIZE),
        "rt": "DAY",
        "tp": "0",
        "ts": symbol,
        "tt": "B" if side == "BUY" else "S",
        "price": str(price)
    }

    payload = f"jData={json.dumps(order_data)}"

    response = requests.post(url, headers=headers, data=payload)

    print("Order Response:", response.text)
    return response.text


# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json
    print("Received:", data)

    action = data.get("action")     # BUY / SELL
    symbol = data.get("symbol")     # OPTION SYMBOL
    price = data.get("price")       # LTP

    if not action or not symbol:
        return jsonify({"error": "Missing data"}), 400

    result = place_order(symbol, action, price)

    return jsonify({"status": "order sent", "response": result})


# ===== HEALTH CHECK =====
@app.route('/')
def home():
    return "Running"
