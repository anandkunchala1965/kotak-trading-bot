import requests
import pyotp
import os

# ENV VARIABLES
MOBILE = os.getenv("MOBILE")
CLIENT_ID = os.getenv("CLIENT_ID")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

BASE_HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# STEP 1 - GENERATE TOTP
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# STEP 2 - LOGIN STEP 1 (VALIDATE)
def login_step1():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    payload = {
        "mobileNumber": MOBILE,
        "ucc": CLIENT_ID,
        "totp": generate_totp()
    }

    res = requests.post(url, json=payload, headers=BASE_HEADERS)

    print("STEP1 STATUS:", res.status_code)
    print("STEP1 RESPONSE:", res.text)

    data = res.json()

    token = data["data"]["token"]
    sid = data["data"]["sid"]

    return token, sid

# STEP 3 - LOGIN STEP 2 (MPIN AUTH)
def login_step2(token, sid):
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiAuthenticate"

    headers = BASE_HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    headers["Sid"] = sid

    payload = {
        "mpin": MPIN
    }

    res = requests.post(url, json=payload, headers=headers)

    print("STEP2 STATUS:", res.status_code)
    print("STEP2 RESPONSE:", res.text)

    data = res.json()

    trade_token = data["data"]["token"]

    return trade_token, sid

# FINAL FUNCTION
def login():
    token, sid = login_step1()
    trade_token, sid = login_step2(token, sid)

    return trade_token, sid
