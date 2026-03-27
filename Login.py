import os
import requests
import pyotp

USER = os.getenv("KOTAK_USERID")
PASSWORD = os.getenv("KOTAK_PASSWORD")
TOTP_SECRET = os.getenv("KOTAK_TOTP_SECRET")

BASE_HEADERS = {
    "Content-Type": "application/json",
    "neo-fin-key": "neotradeapi"
}

def generate_totp():
    return pyotp.TOTP(TOTP_SECRET).now()

def login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    payload = {
        "userId": USER,
        "password": PASSWORD,
        "otp": generate_totp()
    }

    res = requests.post(url, json=payload, headers=BASE_HEADERS)
    print("LOGIN:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Login failed")

    return data["data"]

def validate(login_data):
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    headers = BASE_HEADERS.copy()
    headers.update({
        "Auth": login_data["token"],
        "Sid": login_data["sid"]
    })

    res = requests.post(url, headers=headers)
    print("VALIDATE:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Validation failed")

    return data["data"]

def get_session():
    login_data = login()
    validate_data = validate(login_data)

    return {
        "auth": login_data["token"],
        "sid": login_data["sid"],
        "base_url": validate_data["baseUrl"]
    }
