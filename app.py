from flask import Flask
import requests
import pyotp
import os

app = Flask(__name__)

# ==============================
# ENV VARIABLES (SET IN RENDER)
# ==============================
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

# ==============================
# HEADERS
# ==============================
HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# ==============================
# GENERATE TOTP
# ==============================
def generate_totp():
    if not TOTP_SECRET:
        return "MISSING_TOTP_SECRET"
    try:
        return pyotp.TOTP(TOTP_SECRET).now()
    except Exception as e:
        return f"TOTP_ERROR: {str(e)}"

# ==============================
# STEP 1
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
        return f"STATUS: {res.status_code}\nRESPONSE: {res.text}"
    except Exception as e:
        return f"ERROR: {str(e)}"

# ==============================
# STEP 2
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
        return f"STATUS: {res.status_code}\nRESPONSE: {res.text}"
    except Exception as e:
        return f"ERROR: {str(e)}"

# ==============================
# TEST ROUTE (FINAL)
# ==============================
@app.route('/test-login', strict_slashes=False)
def test_login():

    # Check ENV first
    if not MOBILE or not UCC or not MPIN or not TOTP_SECRET:
        return f"""
ENV VARIABLES MISSING

MOBILE: {MOBILE}
UCC: {UCC}
MPIN: {"SET" if MPIN else None}
TOTP_SECRET: {"SET" if TOTP_SECRET else None}
""", 200, {'Content-Type': 'text/plain'}

    try:
        step1 = login_step1()
        step2 = login_step2()

        return f"""
================ LOGIN RESULT ================

STEP 1:
{step1}

---------------------------------------------

STEP 2:
{step2}

=============================================
""", 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        return f"ERROR:\n{str(e)}", 500, {'Content-Type': 'text/plain'}

# ==============================
# ROOT
# ==============================
@app.route('/')
def home():
    return "Server is LIVE 🚀"
