from flask import Flask, request, jsonify

app = Flask(__name__)

# ===== CONFIG =====
LOT_SIZE = 1   # fixed 1 lot for now

# ===== HELPER =====
def get_atm_strike(price, step=100):
    return round(price / step) * step

# ===== MOCK LTP FETCH (replace with real API later) =====
def get_ltp(symbol):
    # TEMP: use incoming price
    return float(symbol.get("price", 0))

# ===== WEBHOOK =====
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
    except:
        return {"error": "Invalid JSON"}, 400

    print("Received:", data)

    option_type = data.get("type")
    symbol = data.get("symbol")
    price = float(data.get("price", 0))

    if option_type not in ["CE", "PE"]:
        return jsonify({"error": "Invalid type"}), 400

    if price == 0:
        return jsonify({"error": "Price missing"}), 400

    # ===== CLEAN SYMBOL =====
    if ":" in symbol:
        symbol = symbol.split(":")[1]

    symbol = symbol.replace("1!", "")

    # ===== ATM =====
    atm = get_atm_strike(price)

    option_symbol = f"{symbol}_{atm}_{option_type}"

    print("Option Selected:", option_symbol)

    # ===== LTP BASED LIMIT PRICE =====
    ltp = price   # using chart price for now

    limit_price = round(ltp * 1.01, 2)  # buy slightly above LTP

    print("Placing order at:", limit_price)

    # ===== ORDER STRUCTURE (Kotak format later) =====
    order = {
        "symbol": option_symbol,
        "qty": LOT_SIZE,
        "price": limit_price,
        "order_type": "LIMIT",
        "transaction_type": "BUY"
    }

    print("Order:", order)

    # TODO: Integrate Kotak Neo API here

    return {"status": "order_ready", "order": order}, 200


@app.route('/')
def home():
    return "Manual Elliott Bot Running"

    
