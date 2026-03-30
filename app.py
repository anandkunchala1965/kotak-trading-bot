from flask import Flask, jsonify
import requests
import pyotp
import os

app = Flask(__name__)

# ================================
# 🔐 ENV VARIABLES (SET IN RENDER)
# ================================
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

BASE_HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# ================================
# 🔢 GENERATE TOTP
# ================================
def generate_totp():
    if not TOTP_SECRET:
        raise Exception("TOTP_SECRET not set in environment")
    return pyotp.TOTP(TOTP_SECRET).now()

# ================================
# 🔑 STEP 1 - VALIDATE USER
# ================================
def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/validate"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": generate_totp()
    }

    res = requests.post(url, json=payload, headers=BASE_HEADERS)
    
    return {
        "status_code": res.status_code,
        "response": res.json()
    }

# ================================
# 🔑 STEP 2 - COMPLETE LOGIN
# ================================
def login_step2():
    url = "https://mis.kotaksecurities.com/login/1.0/login"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "mpin": MPIN
    }

    res = requests.post(url, json=payload, headers=BASE_HEADERS)

    return {
        "status_code": res.status_code,
        "response": res.json()
    }

# ================================
# 🧪 TEST ROUTE
# ================================

@app.route('/test-login', methods=['GET'])
def test_login():
    try:
        step1 = login_step1()
        step2 = login_step2()

        return jsonify({
            "success": True,
            "step1": step1,
            "step2": step2
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })
