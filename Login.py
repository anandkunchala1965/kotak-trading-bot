import os
import requests
import pyotp

# ===== ENV VARIABLES =====
USER = os.getenv("KOTAK_USERID")
PASSWORD = os.getenv("KOTAK_PASSWORD")
TOTP_SECRET = os.getenv("KOTAK_TOTP_SECRET")

# ===== CONSTANT HEADERS =====
BASE_HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

# ===== GENERATE TOTP =====
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# ===== LOGIN =====
def login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    payload = {
        "userId": USER,
        "password": PASSWORD,
        "otp": generate_totp()
    }

    headers = BASE_HEADERS.copy()
    headers["Authorization"] = f"Bearer {USER}"   # ✅ REQUIRED

    res = requests.post(url, json=payload, headers=headers)
    print("LOGIN RESPONSE:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Login failed")

    return data["data"]


# ===== VALIDATE SESSION =====
def validate(login_data):
    url = "https://mis.kotaksecurities.com/login/1.0/validate"

    headers = BASE_HEADERS.copy()
    headers["Authorization"] = login_data["token"]   # ✅ FIXED
    headers["Sid"] = login_data["sid"]

    res = requests.get(url, headers=headers)
    print("VALIDATE RESPONSE:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Validation failed")

    return data["data"]


# ===== GET SESSION TOKENS =====
def get_session():
    login_data = login()
    validate_data = validate(login_data)

    return {
        "token": login_data["token"],
        "sid": login_data["sid"],
        "base_url": validate_data["baseUrl"]
    }
