from flask import Flask, request, jsonify
import requests
import os
import json
import urllib.parse

app = Flask(__name__)

# ===== CONFIG =====
TOKEN = os.getenv("KOTAK_TOKEN")
BASE_URL = "https://mis.kotaksecurities.com"
LOT_SIZE = 1


# ===== PLACE ORDER FUNCTION =====
def place_order(symbol, side, price):

    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # ===== FINAL CORRECT ORDER STRUCTURE =====
    order_data = {
        "am": "NO",
        "dq": "0",
        "es": "nse_fo",          # F&O segment
        "mp": "0",
        "pc": "MIS",
        "pf": "N",
        "pr": price,             # ✅ number, not string
        "pt": "LMT",
        "qt": str(LOT_SIZE),
        "rt": "DAY",
        "tp": "0",
        "ts": symbol,            # MUST be exact Kotak symbol
        "tt": "B" if side == "BUY" else "S",
        "oi": "I"                # ✅ IMPORTANT FIELD
    }

    payload = urllib.parse.urlencode({
        "jData": json.dumps(order_data)
    })

    response = requests.post(url, headers=headers, data=payload)

    print("========== FINAL DEBUG ==========")
    print("SYMBOL:", symbol)
    print("PRICE:", price)
    print("PAYLOAD:", order_data)
    print("RESPONSE:", response.text)
    print("================================")

    return response.text


# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json
    print("Received:", data)

    action = data.get("action")
    symbol = data.get("symbol")
    price = data.get("price", 0)

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
    return "FINAL BOT RUNNING 🚀"


# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
