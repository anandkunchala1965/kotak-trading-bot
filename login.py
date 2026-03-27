def login():
    url = "https://mis.kotaksecurities.com/login/1.0/tradeApiLogin"

    payload = {
        "mobileNumber": USER,   # your registered mobile number
        "ucc": PASSWORD,        # your client ID (UCC)
        "totp": generate_totp()
    }

    headers = {
        "Content-Type": "application/json",
        "neo-fin-key": "neotradeapi",
        "Authorization": "Bearer YOUR_ACCESS_TOKEN"
    }

    res = requests.post(url, json=payload, headers=headers)

    print("🔐 LOGIN STATUS:", res.status_code)
    print("🔐 LOGIN RESPONSE:", res.text)

    data = res.json()

    if "data" not in data:
        raise Exception("Login failed: " + str(data))

    return data["data"]
