import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render sets this automatically

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

if not RENDER_URL:
    raise ValueError("RENDER_EXTERNAL_URL not set (are you running locally?)")

WEBHOOK_URL = f"{RENDER_URL}/webhook"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
resp = requests.get(url, params={"url": WEBHOOK_URL})

print("Setting webhook:", WEBHOOK_URL)
print("Response:", resp.json())