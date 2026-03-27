from flask import Flask, request, jsonify
import requests
import os
import json
import urllib.parse

app = Flask(__name__)

# ===== LOGIN DETAILS =====
USER_ID = os.getenv("KOTAK_USER")
PASSWORD = os.getenv("KOTAK_PASS")
TOTP = os.getenv("KOTAK_TOTP")   # from Google Authenticator seed

BASE_URL = "https://mis.kotaksecurities.com"
LOT_SIZE = 1

# ===== LOGIN FUNCTION =====
def login():

    url = f"{BASE_URL}/login/1.0/tradeApiLogin"

    payload = {
        "userId": USER_ID,
        "password": PASSWORD,
        "totp": TOTP
    }

    res = requests.post(url, json=payload)
    data = res.json()

    print("LOGIN RESPONSE:", data)

    return data


# ===== PLACE ORDER =====
def place_order(symbol, side, price):

    login_data = login()

    token = login_data.get("token")
    sid = login_data.get("sid")
    auth = login_data.get("auth")

    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "Authorization": f"Bearer {token}",
        "sid": sid,
        "Auth": auth,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/x-www-form-urlencoded"
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

    print("ORDER RESPONSE:", response.text)

    return response.text


# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json
    print("Received:", data)

    action = data.get("action")
    symbol = data.get("symbol")
    price = data.get("price", 0)

    result = place_order(symbol, action, price)

    return jsonify({"result": result})


@app.route('/')
def home():
    return "Auto Login Bot Running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
