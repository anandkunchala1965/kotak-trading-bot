from flask import Flask, request, jsonify
import requests
import os
import json
import pyotp
import threading
import time

app = Flask(__name__)

# =========================
# ENV VARIABLES (SET IN RENDER)
# =========================
USERID = os.environ.get("KOTAK_USERID")
PASSWORD = os.environ.get("KOTAK_PASSWORD")
TOTP_SECRET = os.environ.get("KOTAK_TOTP_SECRET")

AUTH = None
SID = None
BASE_URL = None


# =========================
# LOGIN FUNCTION
# =========================
def login_kotak():
    global AUTH, SID, BASE_URL

    print("🔄 Logging in to Kotak...")

    totp = pyotp.TOTP(TOTP_SECRET).now()

    login_url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    login_payload = {
        "userid": USERID,
        "password": PASSWORD,
        "otp": totp
    }

    headers = {
        "Content-Type": "application/json"
    }

    login_res = requests.post(login_url, json=login_payload, headers=headers)
    print("LOGIN RESPONSE:", login_res.text)

    # Validate API (VERY IMPORTANT)
    validate_url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    validate_res = requests.post(validate_url, headers=headers)
    print("VALIDATE RESPONSE:", validate_res.text)

    data = validate_res.json()

    AUTH = data.get("Auth")
    SID = data.get("Sid")
    BASE_URL = data.get("baseUrl")

    print("✅ TOKENS UPDATED")


# =========================
# AUTO LOGIN LOOP
# =========================
def auto_login_loop():
    while True:
        try:
            login_kotak()
        except Exception as e:
            print("❌ Login Error:", str(e))

        # Refresh every 12 hours
        time.sleep(12 * 60 * 60)


# =========================
# HEALTH CHECK
# =========================
@app.route("/", methods=["GET"])
def home():
    return "Kotak Bot Running 🚀"


# =========================
# WEBHOOK (TRADINGVIEW)
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    global AUTH, SID, BASE_URL

    # Ensure login is available
    if not AUTH or not SID:
        login_kotak()

    data = request.json
    print("Received:", data)

    action = data.get("action")
    symbol = data.get("symbol")
    price = data.get("price", 0)

    # ===== ORDER PAYLOAD =====
    jData = {
        "am": "NO",
        "dq": "0",
        "es": "nse_fo",
        "mp": "0",
        "pc": "MIS",
        "pf": "N",
        "pr": str(price),
        "pt": "L",  # LIMIT
        "qt": "1",
        "rt": "DAY",
        "tp": "0",
        "ts": symbol,
        "tt": "B" if action == "BUY" else "S"
    }

    url = f"{BASE_URL}/quick/order/rule/ms/place"

    headers = {
        "accept": "application/json",
        "Auth": AUTH,
        "Sid": SID,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "jData": json.dumps(jData)
    }

    response = requests.post(url, headers=headers, data=payload)

    print("ORDER RESPONSE:", response.text)

    return jsonify({
        "status": "sent",
        "kotak_response": response.text
    })


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    threading.Thread(target=auto_login_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
