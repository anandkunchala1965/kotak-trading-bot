from flask import Flask, jsonify
import os
import pyotp
import requests

app = Flask(__name__)

# ================================
# ENV VARIABLES
# ================================
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
MOBILE = os.environ.get("MOBILE_NUMBER")
PASSWORD = os.environ.get("PASSWORD")
TOTP_SECRET = os.environ.get("TOTP")

BASE_URL = "https://gw-napi.kotaksecurities.com"

SAFE_MODE = True  # 🔴 KEEP TRUE FIRST

# ================================
# LOGIN FUNCTION
# ================================
def login():
    totp = pyotp.TOTP(TOTP_SECRET).now()

    url = f"{BASE_URL}/login/1.0/tradeApiLogin"

    headers = {
        "Authorization": API_KEY,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    payload = {
        "mobileNumber": MOBILE,
        "password": PASSWORD,
        "totp": totp
    }

    res = requests.post(url, json=payload, headers=headers)
    data = res.json()

    if data.get("data", {}).get("status") != "success":
        return None

    return data.get("data", {}).get("token")


# ================================
# HOME
# ================================
@app.route("/")
def home():
    return "✅ SERVER LIVE"


# ================================
# NIFTY BUY (FINAL)
# ================================
@app.route("/nifty-buy")
def buy():

    # 👉 MANUAL PRICE (for now)
    nifty_price = 22236

    # 👉 ATM strike
    strike = round(nifty_price / 100) * 100

    # 👉 EXPIRY
    symbol = f"NIFTY28APR26{strike}CE"

    order_payload = {
        "exchangeSegment": "nse_fo",
        "product": "MIS",
        "orderType": "MARKET",
        "quantity": "65",
        "validity": "DAY",
        "tradingSymbol": symbol,
        "transactionType": "BUY"
    }

    # ========= SAFE MODE =========
    SAFE_MODE = False   # ✅ INSIDE FUNCTION

    if SAFE_MODE:
        return jsonify({
            "msg": "SAFE MODE ON",
            "symbol": symbol,
            "qty": 65
        })

    # ========= REAL ORDER =========
    token = login()

    if not token:
        return jsonify({"error": "Login failed"})

    order_url = f"{BASE_URL}/orders/1.0/place"

    headers = {
        "Authorization": API_KEY,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json",
        "access-token": token
    }

    res = requests.post(order_url, json=order_payload, headers=headers)

    return jsonify(res.json())


# ================================
# RUN
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
