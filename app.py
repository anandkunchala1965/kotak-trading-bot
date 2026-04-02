from flask import Flask
import os
import pyotp
import json
from neo_api_client import NeoAPI

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
MOBILE_NUMBER = os.environ.get("MOBILE_NUMBER")
PASSWORD = os.environ.get("PASSWORD")
TOTP_SECRET = os.environ.get("TOTP")

SAFE_MODE = False

def login():
    neo = NeoAPI(consumer_key=API_KEY, consumer_secret=API_SECRET)

    neo.login(
        mobilenumber=MOBILE_NUMBER,
        password=PASSWORD
    )

    otp = pyotp.TOTP(TOTP_SECRET).now()
    neo.session_2fa(OTP=otp)

    return neo

@app.route('/')
def home():
    return {"message": "BOT LIVE"}

@app.route('/nifty-buy')
def buy():

    order_payload = {
        "exchangeSegment": "nse_fo",
        "product": "MIS",
        "orderType": "MARKET",
        "quantity": "75",
        "validity": "DAY",
        "tradingSymbol": "NIFTY24APR22200CE",
        "transactionType": "BUY"
    }

    if SAFE_MODE:
        return {"msg": "SAFE MODE ON"}

    try:
        neo = login()

        response = neo.place_order(order_payload)   # ✅ CORRECT

        return {"status": "SUCCESS", "data": response}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
