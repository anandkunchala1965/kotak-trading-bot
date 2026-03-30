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
    try:
        return pyotp.TOTP(TOTP_SECRET).now()
    except:
        return "ERROR_TOTP"

@app.route("/")
def home():
    return "✅ SERVER LIVE"

@app.route("/test-login")
def test_login():
    return "✅ TEST LOGIN ROUTE WORKING"

@app.route("/full-login")
def full_login():

    step1_url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"
    step2_url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    totp = generate_totp()

    payload1 = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": totp
    }

    payload2 = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "mpin": MPIN
    }

    try:
        res1 = requests.post(step1_url, json=payload1, headers=HEADERS)
        res2 = requests.post(step2_url, json=payload2, headers=HEADERS)

        return f"""
        <html><body style='background:black;color:lime'>
        <h2>LOGIN RESULT</h2>

        <h3>STEP 1</h3>
        <pre>{res1.status_code} {res1.text}</pre>

        <h3>STEP 2</h3>
        <pre>{res2.status_code} {res2.text}</pre>

        </body></html>
        """

    except Exception as e:
        return f"ERROR: {str(e)}"
