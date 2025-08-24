import os
import logging
from flask import Flask, request
import requests

# Logging for debugging
logging.basicConfig(level=logging.INFO)

# Flask app
app = Flask(__name__)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # your telegram id
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route('/')
def home():
    return "Telegram Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        # Only allow admin to send links
        if "http" in text or "www" in text:
            if str(data["message"]["from"]["id"]) != str(ADMIN_ID):
                requests.post(f"{BASE_URL}/deleteMessage", json={
                    "chat_id": chat_id,
                    "message_id": data["message"]["message_id"]
                })
                return "Blocked non-admin link", 200

        # Handle /start command
        if text == "/start":
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "Hello! I'm alive and running on Railway 🚀"
            })

    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))