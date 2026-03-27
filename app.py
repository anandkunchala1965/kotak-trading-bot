from flask import Flask, request, jsonify
import requests
import os
import json
import urllib.parse

app = Flask(__name__)

# ===== CONFIG =====
TOKEN = os.getenv("KOTAK_TOKEN")   # Bearer token
SID = os.getenv("KOTAK_SID")       # session id
AUTH = os.getenv("KOTAK_AUTH")     # auth token

BASE_URL = "https://mis.kotaksecurities.com"
LOT_SIZE = 1


def place_order(symbol, side, price):

    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "sid": SID,
        "Auth": AUTH,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/x-www-form-urlencoded",
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

    payload = urllib.parse.urlencode({
        "jData": json.dumps(order_data)
    })

    response = requests.post(url, headers=headers, data=payload)

    print("========== ORDER DEBUG ==========")
    print("RESPONSE:", response.text)
    print("================================")

    return response.text


@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json
    print("Received:", data)

    action = data.get("action")
    symbol = data.get("symbol")
    price = data.get("price", 0)

    result = place_order(symbol, action, price)

    return jsonify({
        "status": "order sent",
        "response": result
    })


@app.route('/')
def home():
    return "Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
