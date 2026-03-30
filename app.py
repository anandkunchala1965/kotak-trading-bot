from flask import Flask, jsonify
from neo_api_client import NeoAPI
import pyotp
import os

app = Flask(__name__)

# ==============================
# 🔐 ENV VARIABLES (SET IN RENDER)
# ==============================

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
MOBILE = os.getenv("MOBILE")
UCC = os.getenv("UCC")
TOTP_SECRET = os.getenv("TOTP_SECRET")
MPIN = os.getenv("MPIN")

# ==============================
# 🔑 LOGIN FUNCTION
# ==============================

def kotak_login():
    try:
        # Initialize client
        client = NeoAPI(
            environment='prod',
            consumer_key=CONSUMER_KEY
        )

        # Generate TOTP
        totp = pyotp.TOTP(TOTP_SECRET).now()

        # Step 1: Login
        login_response = client.totp_login(
            mobile_number=MOBILE,
            ucc=UCC,
            totp=totp
        )

        # Step 2: Validate MPIN
        validate_response = client.totp_validate(
            mpin=MPIN
        )

        return {
            "login": login_response,
            "validate": validate_response
        }

    except Exception as e:
        return {"error": str(e)}

# ==============================
# 🌐 ROUTES
# ==============================

@app.route('/')
def home():
    return "✅ Kotak Trading Bot Running"

@app.route('/test-login', methods=['GET', 'POST'])
def test_login():
    result = kotak_login()
    return jsonify(result)

# ==============================
# 🚀 RUN APP
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
