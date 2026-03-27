from flask import Flask, request, jsonify
import login

app = Flask(__name__)

@app.route('/')
def home():
    return "Kotak bot is running 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("🔥 Webhook triggered")

        # 🔍 DEBUG: confirm correct login file
        print("📂 Using login file:", login.__file__)

        data = request.json
        print("📩 Data received:", data)

        # 🔐 Step 1: Login & get tokens
        tokens = login.kotak_login()
        print("🔑 Tokens received:", tokens)

        return jsonify({
            "status": "success",
            "message": "Login working",
            "tokens": tokens
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
