from flask import Flask
import os
import pyotp
from neo_api_client import NeoAPI

app = Flask(__name__)

# ==============================
# ENV VARIABLES
# ==============================
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
MOBILE_NUMBER = os.environ.get("MOBILE_NUMBER")
PASSWORD = os.environ.get("PASSWORD")
TOTP_SECRET = os.environ.get("TOTP")

# ==============================
# SAFETY SWITCH
# ==============================
SAFE_MODE = True   # 🔴 KEEP TRUE FOR TESTING

# ==============================
# LOGIN FUNCTION
# ==============================
def login():
    neo = NeoAPI(consumer_key=API_KEY, consumer_secret=API_SECRET)

    neo.login(
        mobilenumber=MOBILE_NUMBER,
        password=PASSWORD
    )

    otp = pyotp.TOTP(TOTP_SECRET).now()
    neo.session_2fa(OTP=otp)

    return neo

# ==============================
# HOME
# ==============================
@app.route('/')
def home():
    return {"message": "BOT LIVE"}

# ==============================
# NIFTY BUY (UPDATED)
# ==============================
@app.route('/nifty-buy')
def buy():

    # 🔹 CURRENT NIFTY PRICE (manual for now)
    nifty_price = 22236  

    # 🔹 Calculate ATM strike
    strike = round(nifty_price / 100) * 100

    # 🔹 Correct expiry
    symbol = f"NIFTY28APR26{strike}CE"

    # 🔹 Correct order payload
    order_payload = {
        "exchangeSegment": "nse_fo",
        "product": "MIS",
        "orderType": "MARKET",
        "quantity": "65",
        "validity": "DAY",
        "tradingSymbol": symbol,
        "transactionType": "BUY"
    }

    # ==============================
    # SAFE MODE
    # ==============================
    if SAFE_MODE:
        return {
            "msg": "SAFE MODE ON",
            "symbol": symbol,
            "qty": 65
        }

    try:
        neo = login()

        response = neo.place_order(order_payload)

        return response   # ✅ IMPORTANT FIX

    except Exception as e:
        return {"error": str(e)}

# ==============================
# RUN APP
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
