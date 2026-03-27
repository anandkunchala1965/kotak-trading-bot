import requests

url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

payload = {
    "apiKey": "1cb6f3ad-7fa8-41bb-b0cc-da68887ba759",
    "secretKey": "YOUR_SECRET_KEY",
    "source": "WebAPI",
    "otp": "YOUR_TOTP"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)
