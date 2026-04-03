"""
Kotak Neo Trading Bot - app.py
Uses direct HTTP calls - no SDK required
Dependencies: flask, gunicorn, pyotp, requests

Env vars to set:
CONSUMER_KEY, MOBILE_NUMBER, PASSWORD, MPIN, TOTP_SECRET, SAFE_MODE
"""

import os
import pyotp
import requests
import logging
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)

CONSUMER_KEY  = os.environ.get("CONSUMER_KEY", "")
MOBILE_NUMBER = os.environ.get("MOBILE_NUMBER", "")
PASSWORD      = os.environ.get("PASSWORD", "")
MPIN          = os.environ.get("MPIN", "")
TOTP_SECRET   = os.environ.get("TOTP_SECRET", "")
SAFE_MODE     = os.environ.get("SAFE_MODE", "true").lower() == "true"

BASE_URL = "https://gw-napi.kotaksecurities.com"

_missing = [k for k, v in {
    "CONSUMER_KEY": CONSUMER_KEY,
    "MOBILE_NUMBER": MOBILE_NUMBER,
    "PASSWORD": PASSWORD,
    "MPIN": MPIN,
    "TOTP_SECRET": TOTP_SECRET,
}.items() if not v]

if _missing:
    log.error("ENV ERROR — missing: %s", ", ".join(_missing))
else:
    log.info("All env vars loaded | SAFE_MODE=%s", SAFE_MODE)


def kotak_login():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()
        log.info("TOTP: %s", totp)

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": CONSUMER_KEY,
        }

        r1 = requests.post(
            f"{BASE_URL}/login/1.0/login/v2/validate",
            json={"mobileNumber": MOBILE_NUMBER, "password": PASSWORD},
            headers=headers,
            timeout=15,
        )
        log.info("Step1 status: %s body: %s", r1.status_code, r1.text[:300])

        if r1.status_code != 200:
            log.error("Step1 failed")
            return None

        d1 = r1.json().get("data", {})
        token = d1.get("token", "")
        sid   = d1.get("sid", "")

        headers2 = {**headers, "Authorization": f"Bearer {token}"}

        r2 = requests.post(
            f"{BASE_URL}/login/1.0/login/totp/validate",
            json={"mpin": MPIN},
            headers=headers2,
            timeout=15,
        )
        log.info("Step2 status: %s body: %s", r2.status_code, r2.text[:300])

        if r2.status_code != 200:
            log.error("Step2 failed")
            return None

        d2 = r2.json().get("data", {})
        trading_token = d2.get("token", token)
        sid2          = d2.get("sid", sid)
        server_id     = d2.get("serverId", "")

        log.info("Login SUCCESS")
        return trading_token, sid2, server_id

    except Exception as e:
        log.exception("Login exception: %s", e)
        return None


def place_order(trading_token, sid, server_id, symbol, action, qty,
                exchange="NFO", product="NRML", order_type="MKT"):
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {trading_token}",
            "Sid": sid,
            "Auth": trading_token,
            "neo-fin-key": "neotradeapi",
        }

        payload = {
            "am": "NO",
            "dq": "0",
            "es": exchange,
            "mp": "0",
            "pc": product,
            "pf": "N",
            "pr": "0",
            "pt": order_type,
            "qt": str(qty),
            "rt": "DAY",
            "tp": "0",
            "ts": symbol,
            "tt": "B" if action.upper() == "BUY" else "S",
        }

        r = requests.post(
            f"{BASE_URL}/quick/order/rule/ms/place",
            json=payload,
            headers=headers,
            timeout=15,
        )

        log.info("Order status: %s body: %s", r.status_code, r.text[:300])
        return r.json()

    except Exception as e:
        log.exception("Order exception: %s", e)
        return None


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "kotak-trading-bot live", "safe_mode": SAFE_MODE})


@app.route("/webhook", methods=["POST"])
@app.route("/nifty-buy", methods=["GET", "POST"])
def webhook():
    data       = request.get_json(silent=True) or {}
    action     = data.get("action", "BUY").upper()
    symbol     = data.get("symbol", "")
    qty        = data.get("qty", 1)
    exchange   = data.get("exchange", "NFO")
    product    = data.get("product", "NRML")
    order_type = data.get("order_type", "MKT")

    log.info("Webhook: %s %s x%s", action, symbol, qty)

    if not symbol:
        return jsonify({"error": "symbol missing"}), 400

    if SAFE_MODE:
        log.info("SAFE MODE ON — order blocked")
        return jsonify({"msg": "SAFE MODE ON", "symbol": symbol, "qty": qty})

    creds = kotak_login()
    if not creds:
        return jsonify({"error": "Login failed"}), 500

    trading_token, sid, server_id = creds

    result = place_order(
        trading_token, sid, server_id,
        symbol, action, qty,
        exchange, product, order_type
    )

    if result:
        return jsonify({"msg": "Order placed", "result": result})

    return jsonify({"error": "Order failed"}), 500


@app.route("/test-login", methods=["GET"])
def test_login():
    if _missing:
        return jsonify({"error": f"Missing env vars: {_missing}"}), 500

    creds = kotak_login()
    if creds:
        return jsonify({"msg": "Login successful"})

    return jsonify({"msg": "Login failed — check logs"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
