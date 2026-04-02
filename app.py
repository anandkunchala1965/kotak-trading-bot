from flask import Flask, jsonify
import os
import pyotp
import requests

app = Flask(__name__)

# ================================
# ENV VARIABLES (RENDER)
# ================================
API_KEY = os.environ.get("API_TOKEN")
MOBILE = os.environ.get("UCC")          # UCC (client id)
PASSWORD = os.environ.get("MPIN")       # not used
TOTP_SECRET = os.environ.get("TOTP_SECRET")

BASE_URL = "https://gw-napi.kotaksecurities.com"

SAFE_MODE = True   # KEEP TRUE

# ================================
# LOGIN FUNCTION
# ================================
def login():
    try:
        print("---- LOGIN START ----")

        if not all([API_KEY, MOBILE, TOTP_SECRET]):
            print("ENV ERROR:", API_KEY, MOBILE, TOTP_SECRET)
            return None

        # Generate TOTP
        totp = pyotp.TOTP(TOTP_SECRET).now()
        print("Generated TOTP:", totp)

        headers = {
            "Authorization": f"Bearer {API_KEY}",   # ✅ FIXED
            "Content-Type": "application/json"
        }

        # ======================
        # STEP 1 → requestId
        # ======================
        url1 = f"{BASE_URL}/login/1.0/login"

        payload1 = {
            "loginId": MOBILE
        }

        res1 = requests.post(url1, json=payload1, headers=headers)

        print("STEP1 STATUS:", res1.status_code)
        print("STEP1 RAW:", res1.text)

        # SAFE JSON PARSE
        try:
            data1 = res1.json()
        except:
            print("STEP1 NOT JSON RESPONSE")
            return None

        if "data" not in data1:
            print("Step1 failed:", data1)
            return None

        request_id = data1["data"].get("requestId")

        if not request_id:
            print("No requestId found")
            return None

        # ======================
        # STEP 2 → TOTP verify
        # ======================
        url2 = f"{BASE_URL}/login/1.0/2fa"

        payload2 = {
            "requestId": request_id,
            "otp": totp
        }

        res2 = requests.post(url2, json=payload2, headers=headers)

        print("STEP2 STATUS:", res2.status_code)
        print("STEP2 RAW:", res2.text)

        try:
            data2 = res2.json()
        except:
            print("STEP2 NOT JSON RESPONSE")
            return None

        if "data" not in data2:
            print("Step2 failed:", data2)
            return None

        token = data2["data"].get("token")

        if not token:
            print("No token received")
            return None

        print("LOGIN SUCCESS")
        return token

    except Exception as e:
        print("LOGIN ERROR:", str(e))
        return None


# ================================
# TEST LOGIN
# ================================
@app.route("/test-login")
def test_login():
    token = login()
    if token:
        return jsonify({"msg": "Login SUCCESS"})
    else:
        return jsonify({"error": "Login failed"})


# ================================
# NIFTY BUY (SAFE MODE)
# ================================
@app.route("/nifty-buy")
def buy():
    nifty_price = 22236
    strike = round(nifty_price / 100) * 100
    symbol = f"NIFTY28APR26{strike}CE"

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
        "Authorization": f"Bearer {API_KEY}",
        "x-auth-token": token,
        "Content-Type": "application/json"
    }

    order_payload = {
        "exchangeSegment": "nse_fo",
        "product": "MIS",
        "orderType": "MARKET",
        "quantity": "65",
        "validity": "DAY",
        "tradingSymbol": symbol,
        "transactionType": "BUY"
    }

    res = requests.post(order_url, json=order_payload, headers=headers)

    return jsonify({
        "order_response": res.text
    })


# ================================
# ROOT
# ================================
@app.route("/")
def home():
    return "Kotak Bot Running 🚀"
