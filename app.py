from flask import Flask, jsonify
import requests
import os
import pyotp

app = Flask(__name__)

# ===== ENV VARIABLES =====
CLIENT_ID = os.getenv("CLIENT_ID")        # e.g. L0130
MOBILE = os.getenv("MOBILE")              # e.g. +919000552327
TOTP_SECRET = os.getenv("KOTAK_TOTP_SECRET")

# ===== GENERATE TOTP =====
def generate_totp():
    if not TOTP_SECRET:
        raise Exception("TOTP_SECRET missing")
    return pyotp.TOTP(TOTP_SECRET).now()

# ===== STEP 0: LOGIN =====
def step0_login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    headers = {
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi",
        "Authorization": CLIENT_ID   # 🔥 VERY IMPORTANT
    }

    payload = {
        "mobileNumber": MOBILE,
        "ucc": CLIENT_ID,
        "totp": generate_totp()
    }

    res = requests.post(url, json=payload, headers=headers)

    try:
        data = res.json()
    except:
        data = res.text

    print("STEP 0 STATUS:", res.status_code)
    print("STEP 0 RESPONSE:", data)

    if res.status_code != 200:
        return {
            "error": "Step 0 failed",
            "status_code": res.status_code,
            "response": data
        }

    return data

# ===== ROUTES =====
@app.route("/")
def home():
    return "Kotak API running"

@app.route("/test-login")
def test_login():
    try:
        result = step0_login()

        return jsonify({
            "status": "SUCCESS",
            "data": result
        })

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        }), 500

# ===== RUN =====
if __name__ == "__main__":
    app.run()
