import os
import requests
import pyotp

# ===== ENV VARIABLES =====
USER = os.getenv("KOTAK_USERID")      # your clientId
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

# ===== LOGIN FUNCTION =====
def login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    payload = {
        "clientId": USER,
        "password": PASSWORD,
        "totp": generate_totp()
    }

    headers = BASE_HEADERS.copy()

    res = requests.post(url, json=payload, headers=headers)

    print("🔐 LOGIN STATUS:", res.status_code)
    print("🔐 LOGIN RESPONSE:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Login failed: " + str(data))

    return data["data"]
