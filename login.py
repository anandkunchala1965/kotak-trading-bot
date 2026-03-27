import os
import requests
import pyotp

# ===== ENV VARIABLES =====
USER = os.getenv("KOTAK_USERID")          # mobile number
PASSWORD = os.getenv("KOTAK_PASSWORD")    # UCC (client ID)
TOTP_SECRET = os.getenv("KOTAK_TOTP_SECRET")
ACCESS_TOKEN = os.getenv("KOTAK_ACCESS_TOKEN")

# ===== GENERATE TOTP =====
def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

# ===== LOGIN FUNCTION =====
def login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    payload = {
        "mobileNumber": USER,
        "ucc": PASSWORD,
        "totp": generate_totp()
    }

    headers = {
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    res = requests.post(url, json=payload, headers=headers)

    print("🔐 LOGIN STATUS:", res.status_code)
    print("🔐 LOGIN RESPONSE:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Login failed: " + str(data))

    return data["data"]
