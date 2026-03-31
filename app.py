import os
import requests
import pyotp
from flask import Flask, jsonify

app = Flask(__name__)

# ENV VARIABLES
API_TOKEN = os.getenv("API_TOKEN")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

MOBILE = "+919000552327"
BASE_URL = "https://mis.kotaksecurities.com"

@app.route("/")
def home():
    return "✅ SERVER LIVE"


@app.route("/full-login")
def full_login():
    try:
        # =========================
        # STEP 1: GENERATE TOTP
        # =========================
        totp = pyotp.TOTP(TOTP_SECRET).now()

        url1 = f"{BASE_URL}/login/1.0/tradeApiLogin"

        headers1 = {
            "Authorization": API_TOKEN,
            "neo-fin-key": "neotradeapi",
            "Content-Type": "application/json"
        }

        payload1 = {
            "mobileNumber": MOBILE,
            "ucc": UCC,
            "totp": totp
        }

        res1 = requests.post(url1, json=payload1, headers=headers1)
        data1 = res1.json()

        # 🔴 Extract requestId
        request_id = data1.get("data", {}).get("requestId")

        if not request_id:
            return jsonify({"error": "Step 1 failed", "response": data1})

        # =========================
        # STEP 2: VALIDATE LOGIN
        # =========================
        url2 = f"{BASE_URL}/login/1.0/validateLogin"

        payload2 = {
            "requestId": request_id,
            "mpin": MPIN
        }

        res2 = requests.post(url2, json=payload2, headers=headers1)
        data2 = res2.json()

        # 🔴 Final token
        access_token = data2.get("data", {}).get("token")

        if not access_token:
            return jsonify({"error": "Step 2 failed", "response": data2})

        return jsonify({
            "message": "✅ LOGIN SUCCESS",
            "access_token": access_token
        })

    except Exception as e:
        return jsonify({"error": str(e)})
