import requests
import pyotp
import os

def kotak_login():

    user_id = os.getenv("KOTAK_USERID")
    password = os.getenv("KOTAK_PASSWORD")
    totp_secret = os.getenv("KOTAK_TOTP_SECRET")

    # Generate TOTP
    totp = pyotp.TOTP(totp_secret).now()
    print("🔐 TOTP:", totp)

    # STEP 1: LOGIN
    login_url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    login_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi",
        "Authorization": "Bearer "  # REQUIRED (even if empty)
    }

    login_payload = {
        "userId": user_id,
        "password": password,
        "otp": totp
    }

    login_res = requests.post(login_url, json=login_payload, headers=login_headers)
    print("LOGIN RESPONSE:", login_res.text)

    # STEP 2: VALIDATE
    validate_url = "https://mis.kotaksecurities.com/login/1.0/tradeApiValidate"

    validate_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi"
    }

    validate_payload = {
        "userId": user_id
    }

    validate_res = requests.post(validate_url, json=validate_payload, headers=validate_headers)
    print("VALIDATE RESPONSE:", validate_res.text)

    data = validate_res.json()

    auth = data.get("data", {}).get("token")
    sid = data.get("data", {}).get("sid")
    base_url = data.get("data", {}).get("baseUrl")

    print("✅ AUTH:", auth)
    print("✅ SID:", sid)
    print("✅ BASE URL:", base_url)

    return {
        "auth": auth,
        "sid": sid,
        "baseUrl": base_url
    }
