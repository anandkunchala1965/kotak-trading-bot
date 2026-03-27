from flask import Flask, request, jsonify
import requests
import os
import json
import urllib.parse

app = Flask(__name__)

# ===== CONFIG =====
TOKEN = os.getenv("KOTAK_TOKEN")   # set this in Render ENV
BASE_URL = "https://mis.kotaksecurities.com"
LOT_SIZE = 1


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
        "pt": "LMT",
        "qt": str(LOT_SIZE),
        "rt": "DAY",
        "tp": "0",
        "ts": symbol,
        "tt": "B" if side == "BUY" else "S"
    }

    # ✅ CORRECT ENCODING (MOST IMPORTANT)
    payload = urllib.parse.urlencode({
        "jData": json.dumps(order_data)
    })

    response = requests.post(url, headers=headers, data=payload)

    print("========== ORDER DEBUG ==========")
    print("SYMBOL:", symbol)
    print("SIDE:", side)
    print("PRICE:", price)
    print("RESPONSE:", response.text)
    print("================================")

    return response.text


# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json
    print("Received Alert:", data)

    action = data.get("action")
    symbol = data.get("symbol")
    price = data.get("price")

    # validation
    if not action or not symbol:
        return jsonify({"error": "Missing action/symbol"}), 400

    # fallback price (if not sent)
    if price is None:
        price = 0

    result = place_order(symbol, action, price)

    return jsonify({
        "status": "order sent",
        "broker_response": result
    })


# ===== HEALTH CHECK =====
@app.route('/')
def home():
    return "Kotak Bot Running 🚀"


# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
