from flask import Flask
import requests
import pyotp
import os

app = Flask(__name__)

# ==============================
# 🔐 ENV VARIABLES (SET IN RENDER)
# ==============================
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# ==============================
# 🔑 HEADERS
# ==============================
HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# ==============================
# 🔢 GENERATE TOTP
# ==============================
def generate_totp():
    if not TOTP_SECRET:
        return "TOTP_SECRET missing"
    try:
        return pyotp.TOTP(TOTP_SECRET).now()
    except Exception as e:
        return f"TOTP ERROR: {str(e)}"

# ==============================
# STEP 1 - VALIDATE USER
# ==============================
def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": generate_totp()
    }

    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        return {
            "status_code": res.status_code,
            "response": res.text
        }
    except Exception as e:
        return {"error": str(e)}

# ==============================
# STEP 2 - LOGIN
# ==============================
def login_step2():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "mpin": MPIN
    }

    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        return {
            "status_code": res.status_code,
            "response": res.text
        }
    except Exception as e:
        return {"error": str(e)}

# ==============================
# 🌐 TEST ROUTE
# ==============================
@app.route('/test-login', strict_slashes=False)
def test_login():
    try:
        # check env first
        if not MOBILE or not UCC or not MPIN or not TOTP_SECRET:
            return f"""
            <h3>❌ Missing ENV Variables</h3>
            <pre>
MOBILE: {MOBILE}
UCC: {UCC}
MPIN: {"SET" if MPIN else None}
TOTP_SECRET: {"SET" if TOTP_SECRET else None}
            </pre>
            """

        step1 = login_step1()
        step2 = login_step2()

        return f"""
        <h2>✅ LOGIN DEBUG OUTPUT</h2>
        <pre>
STEP 1:
{step1}

STEP 2:
{step2}
        </pre>
        """

    except Exception as e:
        return f"<h3>ERROR:</h3><pre>{str(e)}</pre>"

# ==============================
# ROOT CHECK
# ==============================
@app.route('/')
def home():
    return "Server is running 🚀"
