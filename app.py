from flask import Flask
import requests
import os

app = Flask(__name__)

# ENV VARIABLES
API_TOKEN = os.getenv("API_TOKEN")
UCC = os.getenv("UCC")
MPIN = os.getenv("MPIN")
TOTP = os.getenv("TOTP")

# ⚠️ PUT YOUR REGISTERED MOBILE NUMBER HERE (WITH +91)
MOBILE = "+91XXXXXXXXXX"

BASE_URL = "https://mis.kotaksecurities.com"


@app.route("/")
def home():
    return "✅ SERVER LIVE"


@app.route("/full-login")
def full_login():
    result = "<h1>🚀 LOGIN RESULT</h1>"

    # =========================
    # STEP 1: TOTP LOGIN
    # =========================
    url1 = f"{BASE_URL}/login/1.0/tradeApiLogin"

    headers1 = {
        "Authorization": API_TOKEN,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json"
    }

    payload1 = {
        "mobileNumber": MOBILE,
        "ucc": UCC,
        "totp": TOTP
    }

    res1 = requests.post(url1, json=payload1, headers=headers1)

    result += "<h2>STEP 1 (TOTP)</h2>"
    result += f"<pre>Status: {res1.status_code}\n{res1.text}</pre>"

    # Extract sid & token
    try:
        data1 = res1.json().get("data", {})
        sid = data1.get("sid")
        token = data1.get("token")

        if not sid or not token:
            return result + "<h3>❌ STEP 1 FAILED (No SID/TOKEN)</h3>"

    except Exception as e:
        return result + f"<h3>❌ STEP 1 ERROR: {str(e)}</h3>"

    # =========================
    # STEP 2: MPIN LOGIN
    # =========================
    url2 = f"{BASE_URL}/login/1.0/tradeApiValidate"

    headers2 = {
        "Authorization": API_TOKEN,
        "neo-fin-key": "neotradeapi",
        "Content-Type": "application/json",
        "Sid": sid,
        "Auth": token
    }

    payload2 = {
        "mpin": MPIN
    }

    res2 = requests.post(url2, json=payload2, headers=headers2)

    result += "<h2>STEP 2 (MPIN)</h2>"
    result += f"<pre>Status: {res2.status_code}\n{res2.text}</pre>"

    return result


if __name__ == "__main__":
    app.run()
