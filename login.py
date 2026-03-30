from flask import Flask, jsonify
import requests
import pyotp
import os

app = Flask(__name__)

# ENV VARIABLES
MOBILE = os.getenv("MOBILE")        # +91XXXXXXXXXX
UCC = os.getenv("UCC")              # Example: L0130
MPIN = os.getenv("MPIN")            # 4 digit MPIN
TOTP_SECRET = os.getenv("TOTP_SECRET")  # From QR code

BASE_HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# STEP 1: Generate TOTP
def generate_totp():
    try:
        return pyotp.TOTP(TOTP_SECRET).now()
    except Exception as e:
        return str(e)

# STEP 2: Login Step 1 (Validate TOTP)
def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": generate_totp()
    }

    try:
        response = requests.post(url, json=payload, headers=BASE_HEADERS)
        return {
            "status_code": response.status_code,
            "response": response.json()
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# STEP 3: Login Step 2 (MPIN Validation)
def login_step2():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiAuthenticate"

    payload = {
        "mpin": MPIN
    }

    try:
        response = requests.post(url, json=payload, headers=BASE_HEADERS)
        return {
            "status_code": response.status_code,
            "response": response.json()
        }
    except Exception as e:
        return {
            "error": str(e)
        }

# TEST ROUTE
@app.route("/test-login", methods=["GET"])
def test_login():
    step1 = login_step1()

    # If step1 fails, return immediately
    if "error" in step1 or step1.get("status_code") != 200:
        return jsonify({
            "step": "step1_failed",
            "details": step1
        })

    step2 = login_step2()

    return jsonify({
        "step1": step1,
        "step2": step2
    })

# ROOT ROUTE
@app.route("/")
def home():
    return "Kotak API Running 🚀"

# REQUIRED FOR RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
