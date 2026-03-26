from flask import Flask, request, jsonify

app = Flask(__name__)

# ================================
# HELPER FUNCTION
# ================================
def get_atm_strike(price):
    return round(price / 50) * 50


# ================================
# WEBHOOK ROUTE
# ================================
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # ===== INPUTS =====
    action = data.get("action")
    symbol = data.get("symbol")
    qty = data.get("qty", 1)
    price = data.get("price")

    # ===== VALIDATIONS =====
    if action not in ["BUY", "SELL"]:
        return jsonify({"error": "Invalid action"}), 400

    allowed_symbols = ["NIFTY", "BANKNIFTY", "CRUDEOIL", "CRUDEOILM"]
    if symbol not in allowed_symbols:
        return jsonify({"error": "Invalid symbol"}), 400

    if price is None:
        return jsonify({"error": "Price required"}), 400

    try:
        price = float(price)
    except:
        return jsonify({"error": "Invalid price"}), 400

    if qty is None or int(qty) > 1:
        return jsonify({
            "error": "Qty too high or missing",
            "allowed_max": 1
        }), 400

    # ===== DETERMINE OPTION TYPE =====
    if action == "BUY":
        option_type = "CE"
    else:
        option_type = "PE"

    # ===== ATM STRIKE =====
    atm_strike = get_atm_strike(price)

    option_symbol = f"{symbol}_{atm_strike}_{option_type}"

    # ===== RESPONSE =====
    return jsonify({
        "status": "success",
        "order": {
            "symbol": option_symbol,
            "qty": qty,
            "side": action,
            "type": "MARKET"
        }
    })


# ================================
# ROOT ROUTE
# ================================
@app.route('/')
def home():
    return "WaveGate Bot Running 🚀"


# ================================
# RUN APP
# ================================
if __name__ == "__main__":
    app.run(debug=True)
