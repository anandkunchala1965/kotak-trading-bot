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
    global access_token

    if access_token is None or (time.time() - last_login_time > 300):
        login()

    return access_token

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    action = data.get("action")
    symbol = data.get("symbol")
    qty = data.get("qty")

    token = get_token()

    order = {
        "symbol": symbol,
        "qty": qty,
        "side": action,
        "type": "MARKET"
    }

    headers = {"Authorization": f"Bearer {token}"}
if TEST_MODE:
    print("TEST MODE ORDER:", order)
    return jsonify({"status": "test_mode", "order": order})

r = requests.post(BASE_URL + "/orders", json=order, headers=headers)
return jsonify(r.json())
