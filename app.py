from flask import Flask, jsonify
import requests
import pyotp
import os

app = Flask(__name__)

# ENV VARIABLES
API_TOKEN = os.getenv("API_TOKEN")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

MOBILE = "+9190000552327"   # your number
BASE_URL = "https://mis.kotaksecurities.com"


@app.route("/")
def home():
    return "✅ SERVER LIVE"


# 🔐 LOGIN FUNCTION (MPIN FLOW - FINAL)
def get_access_token():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()

        headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json"
        }

        # STEP 1: REQUEST LOGIN
        url1 = f"{BASE_URL}/login/1.0/tradeApiLogin"

        payload1 = {
            "mobileNumber": MOBILE,
            "ucc": UCC,
            "totp": totp
        }

        res1 = requests.post(url1, json=payload1, headers=headers)
        data1 = res1.json()

        request_id = data1.get("data", {}).get("requestId")

        if not request_id:
            return None, data1

        # STEP 2: VALIDATE LOGIN WITH MPIN
        url2 = f"{BASE_URL}/login/1.0/validateLogin"

        payload2 = {
            "requestId": request_id,
            "mpin": MPIN
        }

        res2 = requests.post(url2, json=payload2, headers=headers)
        data2 = res2.json()

        token = data2.get("data", {}).get("token")

        if not token:
            return None, data2

        return token, None

    except Exception as e:
        return None, str(e)


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


@app.route("/buy-order")
def buy_order():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()

        # LOGIN AGAIN TO GET TOKEN
        login_url = f"{BASE_URL}/login/1.0/tradeApiLogin"

        headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json"
        }

        login_payload = {
            "mobileNumber": MOBILE,
            "ucc": UCC,
            "totp": totp
        }

        login_res = requests.post(login_url, json=login_payload, headers=headers)
        login_data = login_res.json()

        if login_data.get("data", {}).get("status") != "success":
            return jsonify({"error": "Login failed", "response": login_data})

        access_token = login_data.get("data", {}).get("token")

        # ======================
        # PLACE ORDER
        # ======================

        order_url = f"{BASE_URL}/orders/1.0/place"

        order_headers = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json",
            "access-token": access_token
        }

        order_payload = {
            "exchangeSegment": "nse_cm",
            "product": "MIS",
            "price": "0",
            "orderType": "MARKET",
            "quantity": "1",
            "validity": "DAY",
            "tradingSymbol": "RELIANCE",
            "transactionType": "BUY"
        }

        order_res = requests.post(order_url, json=order_payload, headers=order_headers)
        order_data = order_res.json()

        return jsonify(order_data)

    except Exception as e:
        return jsonify({"error": str(e)})
