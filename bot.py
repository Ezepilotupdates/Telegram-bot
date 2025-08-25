import os
import re
import requests
from flask import Flask, request
from threading import Thread
import time

app = Flask(__name__)

# 🔹 Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", "0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ----------------------------
# 🔹 Helper functions
# ----------------------------
def delete_message(chat_id, message_id):
    requests.post(f"{TELEGRAM_API}/deleteMessage", json={
        "chat_id": chat_id,
        "message_id": message_id
    })

def forward_message(from_chat_id, message_id):
    requests.post(f"{TELEGRAM_API}/forwardMessage", json={
        "chat_id": CHANNEL_ID,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    })

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

# ----------------------------
# 🔹 Webhook (for Render)
# ----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        message_id = msg["message_id"]
        user_id = msg["from"]["id"]
        text = msg.get("text", "")

        # Handle /start
        if text == "/start" and user_id == ADMIN_ID:
            send_message(chat_id, "✅ Bot is running on Render!")

        # Group monitoring
        if chat_id == GROUP_ID:
            if re.search(r"(http://|https://|t\.me|www\.)", text):
                if user_id != ADMIN_ID:  # Only admin can post links
                    delete_message(chat_id, message_id)
                    forward_message(chat_id, message_id)

    return "ok"

@app.route("/")
def home():
    return "Bot is running 🚀"

# ----------------------------
# 🔹 Polling (for local testing)
# ----------------------------
def polling_loop():
    offset = 0
    while True:
        try:
            resp = requests.get(f"{TELEGRAM_API}/getUpdates", params={"offset": offset, "timeout": 30})
            updates = resp.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    message_id = msg["message_id"]
                    user_id = msg["from"]["id"]
                    text = msg.get("text", "")

                    # Handle /start
                    if text == "/start" and user_id == ADMIN_ID:
                        send_message(chat_id, "✅ Bot is running locally (polling)!")

                    # Group monitoring
                    if chat_id == GROUP_ID:
                        if re.search(r"(http://|https://|t\.me|www\.)", text):
                            if user_id != ADMIN_ID:
                                delete_message(chat_id, message_id)
                                forward_message(chat_id, message_id)

        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)

# ----------------------------
# 🔹 Entry point
# ----------------------------
if __name__ == "__main__":
    mode = os.getenv("MODE", "webhook")  # set MODE=polling for local
    port = int(os.getenv("PORT", 5000))

    if mode == "polling":
        print("🤖 Running in POLLING mode...")
        polling_loop()
    else:
        print("🌍 Running in WEBHOOK mode (Render)...")
        app.run(host="0.0.0.0", port=port)