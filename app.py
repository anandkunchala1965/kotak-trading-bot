from flask import Flask, jsonify
import os
import pyotp
import requests

app = Flask(__name__)

# ==============================
# ENV VARIABLES
# ==============================
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
MOBILE = os.environ.get("MOBILE_NUMBER")
PASSWORD = os.environ.get("PASSWORD")
TOTP_SECRET = os.environ.get("TOTP")

BASE_URL = "https://gw-napi.kotaksecurities.com"

SAFE_MODE = True  # 🔴 KEEP TRUE

# ==============================
# LOGIN FUNCTION
# ==============================
def login():
    try:
        print("---- LOGIN START ----")

        # Check env
        if not all([API_KEY, MOBILE, PASSWORD, TOTP_SECRET]):
            print("ENV ERROR:", API_KEY, MOBILE, PASSWORD, TOTP_SECRET)
            return None

        # Generate TOTP
        totp = pyotp.TOTP(TOTP_SECRET).now()
        print("Generated TOTP:", totp)

        # STEP 1 LOGIN
        url = f"{BASE_URL}/login/1.0/tradeApiLogin"

        payload = {
            "mobileNumber": MOBILE,
            "password": PASSWORD
        }

        headers = {
            "Authorization": API_KEY,
            "Content-Type": "application/json"
        }

        res = requests.post(url, json=payload, headers=headers)
        print("Login RAW:", res.text)

        data = res.json()

        if "data" not in data:
            print("Login failed at step 1")
            return None

        request_id = data["data"]["requestId"]
        print("Request ID:", request_id)

        # STEP 2 2FA
        url_2fa = f"{BASE_URL}/login/1.0/2fa"

        payload_2fa = {
            "requestId": request_id,
            "otp": totp
        }

        res2 = requests.post(url_2fa, json=payload_2fa, headers=headers)
        print("2FA RAW:", res2.text)

        data2 = res2.json()

        if "data" not in data2:
            print("2FA failed")
            return None

        token = data2["data"]["accessToken"]
        print("Login SUCCESS")

        return token

    except Exception as e:
        print("Login Exception:", str(e))
        return None

# ==============================
# HOME
# ==============================
@app.route("/")
def home():
    return {"message": "BOT LIVE"}

# ==============================
# TEST LOGIN
# ==============================
@app.route("/test-login")
def test_login():
    token = login()
    if not token:
        return {"error": "Login failed"}
    return {"token": token}

# ==============================
# BUY ORDER
# ==============================
@app.route("/nifty-buy")
def buy():
    try:
        nifty_price = 22236
        strike = round(nifty_price / 100) * 100
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

        # SAFE MODE
        if SAFE_MODE:
            return jsonify({
                "msg": "SAFE MODE ON",
                "symbol": symbol,
                "qty": 65
            })

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

    except Exception as e:
        return jsonify({"error": str(e)})

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
