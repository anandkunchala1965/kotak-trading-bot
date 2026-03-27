from flask import Flask, request, jsonify
from login import kotak_login

app = Flask(__name__)

@app.route('/')
def home():
    return "Kotak bot is running 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        print("🔥 Webhook triggered")

        data = request.json
        print("📩 Data received:", data)

        tokens = kotak_login()

        print("🔑 Tokens:", tokens)

        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
