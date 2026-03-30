from flask import Flask
import requests
import pyotp
import os

app = Flask(__name__)

# =========================
# ENV VARIABLES
# =========================
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# =========================
# GENERATE TOTP
# =========================
def generate_totp():
    try:
        if not TOTP_SECRET:
            return "TOTP_SECRET_MISSING"
        return pyotp.TOTP(TOTP_SECRET).now()
    except Exception as e:
        return f"TOTP_ERROR: {str(e)}"

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "✅ SERVER LIVE"

# =========================
# TEST ROUTE
# =========================
@app.route("/test-login")
def test_login():
    return "✅ TEST LOGIN ROUTE WORKING"

# =========================
# FULL LOGIN ROUTE
# =========================
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
        <html>
        <body style="background:black;color:lime;font-size:16px;">
        
        <h2>🚀 LOGIN RESULT</h2>

        <h3>STEP 1 (TOTP VALIDATION)</h3>
        <pre>Status: {res1.status_code}</pre>
        <pre>{res1.text}</pre>

        <hr>

        <h3>STEP 2 (MPIN LOGIN)</h3>
        <pre>Status: {res2.status_code}</pre>
        <pre>{res2.text}</pre>

        </body>
        </html>
        """

    except Exception as e:
        return f"""
        <html>
        <body style="background:black;color:red;">
        <h2>ERROR OCCURRED</h2>
        <pre>{str(e)}</pre>
        </body>
        </html>
        """

# =========================
# RUN (for local testing)
# =========================
if __name__ == "__main__":
    app.run(debug=True)
