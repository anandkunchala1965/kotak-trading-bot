from flask import Flask, jsonify
import requests
import pyotp
import os

app = Flask(__name__)

# ENV VARIABLES
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

BASE_HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": generate_totp()
    }

    res = requests.post(url, json=payload, headers=BASE_HEADERS)

    return {
        "status": res.status_code,
        "data": res.json()
    }

def login_step2():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiAuthenticate"

    payload = {
        "mpin": MPIN
    }

    res = requests.post(url, json=payload, headers=BASE_HEADERS)

    return {
        "status": res.status_code,
        "data": res.json()
    }

@app.route("/test-login")
def test_login():
    step1 = login_step1()

    if step1["status"] != 200:
        return jsonify({
            "error": "Step1 failed",
            "details": step1
        })

    step2 = login_step2()

    return jsonify({
        "step1": step1,
        "step2": step2
    })

@app.route("/")
def home():
    return "Running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
