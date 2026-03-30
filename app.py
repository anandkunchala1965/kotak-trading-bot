from flask import Flask
import requests
import pyotp
import os

app = Flask(__name__)

# ENV VARIABLES
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

def generate_totp():
    if not TOTP_SECRET:
        return "MISSING_TOTP_SECRET"
    try:
        return pyotp.TOTP(TOTP_SECRET).now()
    except Exception as e:
        return f"TOTP_ERROR: {str(e)}"

def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"
    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": generate_totp()
    }
    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        return f"STATUS: {res.status_code}\n{res.text}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def login_step2():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"
    payload = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "mpin": MPIN
    }
    try:
        res = requests.post(url, json=payload, headers=HEADERS)
        return f"STATUS: {res.status_code}\n{res.text}"
    except Exception as e:
        return f"ERROR: {str(e)}"

@app.route('/test-login')
def test_login():

    if not MOBILE or not UCC or not MPIN or not TOTP_SECRET:
        return f"""
        <h2 style="color:red;">ENV VARIABLES MISSING</h2>
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
    <html>
    <body style="background:black;color:lime;font-size:18px;">
    <h2>LOGIN RESULT</h2>

    <h3>STEP 1</h3>
    <pre>{step1}</pre>

    <h3>STEP 2</h3>
    <pre>{step2}</pre>

    </body>
    </html>
    """

@app.route('/')
def home():
    return "Server is LIVE 🚀"
