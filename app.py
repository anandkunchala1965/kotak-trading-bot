from flask import Flask, request, jsonify
import os
import requests

app = Flask(name)

# ===== CONFIG =====
TOKEN = os.getenv("KOTAK_TOKEN")
LOT_SIZE = 1  # 1 lot only

# ===== HELPER =====
def get_atm_strike(price, step=100):
    return round(price / step) * step

# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
    except:
        return {"error": "Invalid JSON"}, 400

    print("Received:", data)
    print("TOKEN:", TOKEN)

    action = data.get("action")   # BUY or SELL
    symbol = data.get("symbol")   # NIFTY / BANKNIFTY / CRUDEOIL
    price = float(data.get("price", 0))

    if action not in ["BUY", "SELL"]:
        return {"error": "Invalid action"}, 400

    if symbol not in ["NIFTY", "BANKNIFTY", "CRUDEOIL"]:
        return {"error": "Invalid symbol"}, 400

    if price == 0:
        return {"error": "Price missing"}, 400

    # ===== LOGIC =====
    option_type = "CE" if action == "BUY" else "PE"
    atm_strike = get_atm_strike(price)

    option_symbol = f"{symbol}{atm_strike}{option_type}"
    print("Trading:", option_symbol)

    # ===== HEADERS =====
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # ===== ORDER PAYLOAD (EDIT IF NEEDED LATER) =====
    order_data = {
        "symbol": option_symbol,
        "qty": LOT_SIZE,
        "orderType": "LIMIT",
        "price": price,   # LTP based
        "transactionType": "BUY",
        "product": "MIS"
    }

    print("Order Data:", order_data)

    # ===== API CALL =====
    try:
        response = requests.post(
            "https://api.kotak.com/trade/order",  # ⚠️ confirm endpoint later
            json=order_data,
            headers=headers
        )
        print("API Response:", response.text)

    except Exception as e:
        print("API Error:", str(e))
        return {"error": "API failed"}, 500

    return {"status": "order sent"}, 200


@app.route('/')
def home():
    return "Running"
