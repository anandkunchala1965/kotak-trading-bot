import os
import requests
import pyotp
from flask import Flask, jsonify

app = Flask(__name__)

# =========================
# ENV VARIABLES
# =========================
API_TOKEN = os.getenv("API_TOKEN")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

MOBILE = "+919000552327"
BASE_URL = "https://mis.kotaksecurities.com"

# =========================
# SAFE MODE (IMPORTANT)
# =========================
SAFE_MODE = False

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "✅ SERVER LIVE"

# =========================
# LOGIN
# =========================
@app.route("/full-login")
def full_login():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()

        url = f"{BASE_URL}/login/1.0/tradeApiLogin"

        headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json"
        }

        payload = {
            "mobileNumber": MOBILE,
            "ucc": UCC,
            "totp": totp
        }

        res = requests.post(url, json=payload, headers=headers)
        data = res.json()

        if data.get("data", {}).get("status") != "success":
            return jsonify({
                "error": "Login failed",
                "response": data
            })

        token = data.get("data", {}).get("token")

        return jsonify({
            "message": "LOGIN SUCCESS",
            "access_token": token
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# NIFTY BUY (SAFE)
# =========================
@app.route("/nifty-buy")
def nifty_buy():
    try:
        # STEP 1: LOGIN
        totp = pyotp.TOTP(TOTP_SECRET).now()

        login_url = f"{BASE_URL}/login/1.0/tradeApiLogin"

        headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json"
        }

        payload = {
            "mobileNumber": MOBILE,
            "ucc": UCC,
            "totp": totp
        }

        login_res = requests.post(login_url, json=payload, headers=headers)
        login_data = login_res.json()

        if login_data.get("data", {}).get("status") != "success":
            return jsonify({
                "error": "Login failed",
                "response": login_data
            })

        access_token = login_data.get("data", {}).get("token")

        # STEP 2: PREPARE ORDER
        order_payload = {
    "exchangeSegment": "nse_fo",
    "product": "MIS",
    "orderType": "MARKET",
    "quantity": "1",
    "validity": "DAY",
    "tradingSymbol": "NIFTY24APR22200CE",
    "transactionType": "BUY"
}

        # =========================
        # SAFE MODE BLOCK
        # =========================
        if SAFE_MODE:
            return jsonify({
                "message": "SAFE MODE ON - Order NOT placed",
                "order_payload": order_payload
            })

        # =========================
        # REAL ORDER (WILL NOT RUN NOW)
        # =========================
        order_url = f"{BASE_URL}/orders/1.0/place"

        order_headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json",
            "access-token": access_token
        }

        order_res = requests.post(order_url, json=order_payload, headers=order_headers)
        order_data = order_res.json()

        return jsonify(order_data)

    except Exception as e:
        return jsonify({"error": str(e)})
