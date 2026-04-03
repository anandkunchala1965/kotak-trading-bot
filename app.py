“””
Kotak Neo Trading Bot - app.py
Handles ATM options for MCX Crude Oil and Nifty/BankNifty
Uses direct HTTP calls - no SDK required
Dependencies: flask, gunicorn, pyotp, requests
“””

import os
import pyotp
import requests
import logging
from datetime import datetime
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO, format=”%(asctime)s %(levelname)s %(message)s”)
log = logging.getLogger(**name**)

app = Flask(**name**)

CONSUMER_KEY   = os.environ.get(“CONSUMER_KEY”, “”)
MOBILE_NUMBER  = os.environ.get(“MOBILE_NUMBER”, “”)
PASSWORD       = os.environ.get(“PASSWORD”, “”)
MPIN           = os.environ.get(“MPIN”, “”)
TOTP_SECRET    = os.environ.get(“TOTP_SECRET”, “”)
SAFE_MODE      = os.environ.get(“SAFE_MODE”, “true”).lower() == “true”

BASE_URL = “https://gw-napi.kotaksecurities.com”

_missing = [k for k, v in {
“CONSUMER_KEY”: CONSUMER_KEY,
“MOBILE_NUMBER”: MOBILE_NUMBER,
“PASSWORD”: PASSWORD,
“MPIN”: MPIN,
“TOTP_SECRET”: TOTP_SECRET,
}.items() if not v]

if _missing:
log.error(“ENV ERROR - missing: %s”, “, “.join(_missing))
else:
log.info(“All env vars loaded | SAFE_MODE=%s”, SAFE_MODE)

# ── Strike rounding ──────────────────────────────────────────

STRIKE_STEP = {
“CRUDEOIL”:  100,
“CRUDEOILM”: 100,
“NIFTY”:      50,
“BANKNIFTY”:  100,
}

# ── Expiry helpers ───────────────────────────────────────────

MONTH_MAP = [“JAN”,“FEB”,“MAR”,“APR”,“MAY”,“JUN”,
“JUL”,“AUG”,“SEP”,“OCT”,“NOV”,“DEC”]

def current_expiry_str():
“”“Returns e.g. ‘25APR’ for April 2025”””
now = datetime.now()
yy  = str(now.year)[2:]
mon = MONTH_MAP[now.month - 1]
return f”{yy}{mon}”

def atm_strike(ltp, instrument):
step = STRIKE_STEP.get(instrument.upper(), 50)
return int(round(ltp / step) * step)

# ── Symbol builders ──────────────────────────────────────────

def build_option_symbol(instrument, option_type, strike):
“””
Kotak Neo symbol format examples:
CRUDEOIL25APR5200CE  (MCX)
NIFTY25APR22500CE    (NFO)
“””
expiry = current_expiry_str()
inst   = instrument.upper()
ot     = option_type.upper()
return f”{inst}{expiry}{strike}{ot}”

# ── Exchange mapping ─────────────────────────────────────────

EXCHANGE_MAP = {
“CRUDEOIL”:  “MCX”,
“CRUDEOILM”: “MCX”,
“NIFTY”:     “NFO”,
“BANKNIFTY”: “NFO”,
}

# ── LTP fetch ────────────────────────────────────────────────

def get_ltp(instrument, trading_token, sid, server_id):
“”“Fetch LTP for the underlying to compute ATM strike.”””
# Underlying token map (Kotak scrip tokens for LTP)
SCRIP_MAP = {
“CRUDEOIL”:  {“exchange”: “MCX”,  “token”: “MCX:CRUDEOIL25APRFUT”},
“CRUDEOILM”: {“exchange”: “MCX”,  “token”: “MCX:CRUDEOILM25APRFUT”},
“NIFTY”:     {“exchange”: “NSE”,  “token”: “NSE:NIFTY 50”},
“BANKNIFTY”: {“exchange”: “NSE”,  “token”: “NSE:NIFTY BANK”},
}
info = SCRIP_MAP.get(instrument.upper())
if not info:
log.error(“Unknown instrument: %s”, instrument)
return None
try:
headers = {
“accept”: “application/json”,
“Authorization”: f”Bearer {trading_token}”,
“Sid”: sid,
“Auth”: trading_token,
“neo-fin-key”: “neotradeapi”,
}
r = requests.get(
f”{BASE_URL}/market-data/1.0/quote/ltp”,
params={“symbol”: info[“token”]},
headers=headers,
timeout=10,
)
data = r.json()
ltp = float(data.get(“data”, {}).get(“ltp”, 0))
log.info(“LTP for %s: %s”, instrument, ltp)
return ltp
except Exception as e:
log.exception(“LTP fetch error: %s”, e)
return None

# ── Login ────────────────────────────────────────────────────

def kotak_login():
try:
totp = pyotp.TOTP(TOTP_SECRET).now()
log.info(“TOTP: %s”, totp)

```
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

    d1  = r1.json().get("data", {})
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

    d2          = r2.json().get("data", {})
    trading_token = d2.get("token", token)
    sid2          = d2.get("sid", sid)
    server_id     = d2.get("serverId", "")

    log.info("Login SUCCESS")
    return trading_token, sid2, server_id

except Exception as e:
    log.exception("Login exception: %s", e)
    return None
```

# ── Place order ──────────────────────────────────────────────

def place_order(trading_token, sid, server_id, symbol, action, qty,
exchange=“NFO”, product=“NRML”, order_type=“MKT”):
try:
headers = {
“accept”: “application/json”,
“Content-Type”: “application/json”,
“Authorization”: f”Bearer {trading_token}”,
“Sid”: sid,
“Auth”: trading_token,
“neo-fin-key”: “neotradeapi”,
}

```
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
```

# ── Routes ───────────────────────────────────────────────────

@app.route(”/”, methods=[“GET”])
def home():
return jsonify({“status”: “kotak-trading-bot live”, “safe_mode”: SAFE_MODE})

@app.route(”/webhook”, methods=[“POST”])
def webhook():
data        = request.get_json(silent=True) or {}
action      = data.get(“action”, “BUY”).upper()
instrument  = data.get(“instrument”, “”).upper()   # CRUDEOIL / NIFTY / BANKNIFTY
option_type = data.get(“option_type”, “”).upper()  # CE or PE
qty         = data.get(“quantity”, 1)

```
log.info("Webhook: %s %s %s qty=%s", action, instrument, option_type, qty)

if not instrument:
    return jsonify({"error": "instrument missing"}), 400
if option_type not in ("CE", "PE"):
    return jsonify({"error": "option_type must be CE or PE"}), 400

if SAFE_MODE:
    log.info("SAFE MODE ON - order blocked")
    return jsonify({"msg": "SAFE MODE ON", "instrument": instrument,
                    "option_type": option_type, "qty": qty})

creds = kotak_login()
if not creds:
    return jsonify({"error": "Login failed"}), 500

trading_token, sid, server_id = creds

# Fetch LTP to determine ATM strike
ltp = get_ltp(instrument, trading_token, sid, server_id)
if not ltp:
    return jsonify({"error": "LTP fetch failed"}), 500

strike   = atm_strike(ltp, instrument)
symbol   = build_option_symbol(instrument, option_type, strike)
exchange = EXCHANGE_MAP.get(instrument, "NFO")

log.info("Placing order: %s %s strike=%s symbol=%s", action, instrument, strike, symbol)

result = place_order(trading_token, sid, server_id, symbol, action, qty,
                     exchange=exchange)

if result:
    return jsonify({"msg": "Order placed", "symbol": symbol,
                    "strike": strike, "ltp": ltp, "result": result})

return jsonify({"error": "Order failed"}), 500
```

@app.route(”/test-login”, methods=[“GET”])
def test_login():
if _missing:
return jsonify({“error”: f”Missing env vars: {_missing}”}), 500
creds = kotak_login()
if creds:
return jsonify({“msg”: “Login successful”})
return jsonify({“msg”: “Login failed - check logs”}), 500

if **name** == “**main**”:
app.run(host=“0.0.0.0”, port=10000)
