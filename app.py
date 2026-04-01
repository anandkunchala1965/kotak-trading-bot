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
