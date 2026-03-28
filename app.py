from flask import Flask
from login import login

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

@app.route("/test-login")
def test_login():
    token, sid = login()
    return {
        "token": token,
        "sid": sid
    }
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("🔥 Webhook triggered")

        # 🔍 DEBUG: confirm correct login file
        print("📂 Using login file:", login.__file__)

        data = request.json
        print("📩 Data received:", data)

        # 🔐 Step 1: Login & get tokens
        tokens = login.login()
        print("🔑 Tokens received:", tokens)

        return jsonify({
            "status": "success",
            "message": "Login working",
            "tokens": tokens
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
