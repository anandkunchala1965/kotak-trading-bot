from flask import Flask, jsonify
import requests
import os
import pyotp

app = Flask(__name__)

# ===== ENV VARIABLES =====
CLIENT_ID = os.getenv("CLIENT_ID")
MOBILE = os.getenv("MOBILE")
TOTP_SECRET = os.getenv("KOTAK_TOTP_SECRET")

# ===== GENERATE TOTP =====
def generate_totp():
    if not TOTP_SECRET:
        raise Exception("TOTP_SECRET missing")
    return pyotp.TOTP(TOTP_SECRET).now()

# ===== STEP 0: TRADE API LOGIN =====
def step0_login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    headers = {
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi"
    }

    payload = {
        "mobileNumber": MOBILE,
        "ucc": CLIENT_ID,
        "totp": generate_totp()
    }

    res = requests.post(url, json=payload, headers=headers)
    data = res.json()

    print("STEP 0 STATUS:", res.status_code)
    print("STEP 0 RESPONSE:", data)

    if res.status_code != 200:
        raise Exception("Step 0 failed")

    return data

# ===== TEST ROUTE =====
@app.route("/")
def home():
    return "Kotak API running"

@app.route("/test-login")
def test_login():
    try:
        step0_data = step0_login()

        return jsonify({
            "status": "SUCCESS",
            "step0": step0_data
        })

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run()
