from flask import Flask, request, jsonify
import requests
import pyotp
import time

app = Flask(__name__)

API_KEY = "your_api_key"
USER_ID = "your_user_id"
PASSWORD = "your_password"
TOTP_SECRET = "your_totp_secret"

BASE_URL = "https://api.kotaksecurities.com"
TEST_MODE = True
access_token = None
last_login_time = 0

def login():
    global access_token, last_login_time

    totp = pyotp.TOTP(TOTP_SECRET).now()

    r = requests.post(BASE_URL + "/login", json={
        "userid": USER_ID,
        "password": PASSWORD,
        "totp": totp
    })

    data = r.json()
    access_token = data.get("access_token")
    last_login_time = time.time()

def get_token():
    global access_token, last_login_time

    if access_token is None or (time.time() - last_login_time > 300):
        login()
    return access_token

@app.route('/webhook', methods=['POST'])
def webhook():
        data = request.json

        action = data.get("action")
        symbol = data.get("symbol")
        qty = data.get("qty")

        # token = get_token()   # disabled for testing

        order = {
        "symbol": symbol,
        "qty": qty,
        "side": action,
        "type": "MARKET"
     }
    
    return jsonify({
        "status": "received",
        "order": order
    })
