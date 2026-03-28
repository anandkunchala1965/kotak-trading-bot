from flask import Flask, jsonify
import requests
import os
import pyotp

app = Flask(__name__)

# ========= ENV VARIABLES =========
CLIENT_ID = os.getenv("CLIENT_ID")
MOBILE = os.getenv("MOBILE")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# ========= GENERATE TOTP =========
def generate_totp():
    if not TOTP_SECRET:
        raise Exception("TOTP_SECRET missing")
    return pyotp.TOTP(TOTP_SECRET).now()

# ========= LOGIN STEP 1 =========
def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/login/v2/validate"

    headers = {
        "Content-Type": "application/json",
        "Authorization": CLIENT_ID   # ✅ REQUIRED (no Bearer)
    }

    payload = {
        "mobileNumber": MOBILE,
        "totp": generate_totp()
    }

    response = requests.post(url, json=payload, headers=headers)

    print("STEP1 STATUS:", response.status_code)
    print("STEP1 RESPONSE:", response.text)

    data = response.json()

    if "data" not in data:
        raise Exception(f"STEP1 FAILED: {data}")

    token = data["data"]["token"]
    sid = data["data"]["sid"]

    return token, sid

# ========= LOGIN STEP 2 =========
def login_step2(token, sid):
    url = "https://mis.kotaksecurities.com/login/1.0/login/v2/validateMPIN"

    headers = {
        "Content-Type": "application/json",
        "Authorization": CLIENT_ID,
        "Sid": sid,
        "Auth": token
    }

    payload = {
        "mpin": MPIN
    }

    response = requests.post(url, json=payload, headers=headers)

    print("STEP2 STATUS:", response.status_code)
    print("STEP2 RESPONSE:", response.text)

    data = response.json()

    if "data" not in data:
        raise Exception(f"STEP2 FAILED: {data}")

    return data["data"]

# ========= FULL LOGIN =========
def login():
    token, sid = login_step1()
    return login_step2(token, sid)

# ========= TEST ROUTE =========
@app.route("/test-login")
def test_login():
    try:
        result = login()
        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ========= ROOT =========
@app.route("/")
def home():
    return "Kotak Trading Bot Running 🚀"
