import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not set in environment variables!")

# Create the Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Flask app for Render
app = Flask(__name__)

# --- Telegram Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello 👋, I am alive on Render!")

application.add_handler(CommandHandler("start", start))

# --- Flask Routes ---
@app.route("/")
def home():
    return "Bot is running on Render!"

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return {"ok": True}

# --- Main entrypoint ---
if __name__ == "__main__":
    if os.getenv("RENDER"):  
        # On Render → use Flask (Gunicorn will run `bot:app`)
        print("🚀 Running with webhook on Render...")
    else:
        # Local development → use polling
        print("🤖 Running locally with polling...")
        application.run_polling()