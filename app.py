from flask import Flask, request, jsonify
import requests
import pyotp
import time

app = Flask(__name__)

# ==============================
# CONFIG (Fill your details)
# ==============================
API_KEY = "your_api_key"
USER_ID = "your_user_id"
PASSWORD = "your_password"
TOTP_SECRET = "your_totp_secret"
BASE_URL = "https://api.kotak.com"   # check actual Kotak API URL

access_token = None
last_login_time = 0

# ==============================
# LOGIN FUNCTION
# ==============================
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

# ==============================
# TOKEN HANDLER
# ==============================
def get_token():
    global access_token, last_login_time

    if access_token is None or (time.time() - last_login_time > 300):
        login()

    return access_token

# ==============================
# WEBHOOK (MAIN BOT)
# ==============================
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    action = data.get("action")
    symbol = data.get("symbol")
    qty = data.get("qty")

    # ==============================
    # SAFETY RULES
    # ==============================

    # 1. MAX QTY LIMIT
    if qty is None or int(qty) > 1:
        return jsonify({
            "error": "Qty too high or missing",
            "allowed_max": 1
        }), 400

    # 2. ALLOWED SYMBOLS
    allowed_symbols = ["NIFTY", "BANKNIFTY"]
    if symbol not in allowed_symbols:
        return jsonify({
            "error": "Invalid symbol",
            "allowed": allowed_symbols
        }), 400

    # 3. ACTION VALIDATION
    if action not in ["BUY", "SELL"]:
        return jsonify({
            "error": "Invalid action",
            "allowed": ["BUY", "SELL"]
        }), 400

    # ==============================
    # CREATE ORDER
    # ==============================
    order = {
        "symbol": symbol,
        "qty": int(qty),
        "side": action,
        "type": "MARKET"
    }

    # ==============================
    # (OPTIONAL) LIVE ORDER EXECUTION
    # ==============================
    # Uncomment below ONLY when ready

    """
    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        BASE_URL + "/orders",
        json=order,
        headers=headers
    )

    return jsonify(response.json())
    """

    # ==============================
    # TEST MODE RESPONSE
    # ==============================
    return jsonify({
        "status": "received",
        "order": order
    })
