from flask import Flask, jsonify
import requests
import pyotp
import os

app = Flask(__name__)

# ENV VARIABLES
API_TOKEN = os.getenv("API_TOKEN")
UCC = os.getenv("UCC")
TOTP_SECRET = os.getenv("TOTP_SECRET")

MOBILE = "+919000055237"   # your number
BASE_URL = "https://mis.kotaksecurities.com"


@app.route("/")
def home():
    return "✅ SERVER LIVE"


# 🔐 LOGIN
def get_access_token():
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
        return None, data

    token = data.get("data", {}).get("token")
    return token, None


@app.route("/full-login")
def full_login():
    try:
        token, error = get_access_token()

        if error:
            return jsonify({"error": "Login failed", "response": error})

        return jsonify({
            "message": "LOGIN SUCCESS",
            "access_token": token
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/nifty-buy")
def nifty_buy():
    try:
        # STEP 1: LOGIN
        access_token, error = get_access_token()

        if error:
            return jsonify({"error": "Login failed", "response": error})

        # STEP 2: PLACE ORDER
        order_url = f"{BASE_URL}/orders/1.0/place"

        order_headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json",
            "access-token": access_token
        }

        order_payload = {
            "exchangeSegment": "nse_fo",
            "product": "MIS",
            "orderType": "MARKET",
            "quantity": "1",   # 🔴 FIRST TEST WITH 1
            "validity": "DAY",
            "tradingSymbol": "NIFTY07APR22700CE",
            "transactionType": "BUY"
        }

        order_res = requests.post(order_url, json=order_payload, headers=order_headers)

        return jsonify(order_res.json())

    except Exception as e:
        return jsonify({"error": str(e)})
