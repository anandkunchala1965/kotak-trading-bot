from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# =========================
# ENV VARIABLES (SET IN RENDER)
# =========================
AUTH = os.environ.get("KOTAK_AUTH")
SID = os.environ.get("KOTAK_SID")
BASE_URL = os.environ.get("KOTAK_BASE_URL")  # from login response

# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def home():
    return "Kotak Trading Bot Running 🚀"


# =========================
# WEBHOOK (TRADINGVIEW)
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    print("Received:", data)

    action = data.get("action")  # BUY / SELL
    symbol = data.get("symbol")
    price = data.get("price", 0)

    # =========================
    # BUILD jData (IMPORTANT)
    # =========================
    jData = {
        "am": "NO",
        "dq": "0",
        "es": "nse_fo",
        "mp": "0",
        "pc": "MIS",
        "pf": "N",
        "pr": str(price),           # LIMIT price
        "pt": "L",                  # L = LIMIT (use MKT if needed)
        "qt": "1",
        "rt": "DAY",
        "tp": "0",
        "ts": symbol,               # VERY IMPORTANT
        "tt": "B" if action == "BUY" else "S"
    }

    print("FINAL PAYLOAD:", jData)

    # =========================
    # API CALL
    # =========================
    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "accept": "application/json",
        "Auth": AUTH,
        "Sid": SID,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "jData": json.dumps(jData)   # 🔥 THIS FIXES YOUR ERROR
    }

    response = requests.post(url, headers=headers, data=payload)

    print("RESPONSE:", response.text)

    return jsonify({
        "status": "sent",
        "kotak_response": response.json()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
