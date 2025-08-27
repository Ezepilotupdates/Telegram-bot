import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not set!")

# Telegram app
application = Application.builder().token(BOT_TOKEN).build()

# Flask app
app = Flask(__name__)

# --- Security Handler ---
async def block_non_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch unauthorized users and alert admin."""
    user = update.effective_user
    if user:
        msg = f"🚨 Unauthorized access attempt!\n\nUser: {user.full_name}\nID: {user.id}"
        logger.warning(msg)
        # Notify admin
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

# --- Commands (Admin only) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Welcome Admin, bot is alive on Render!")

async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) or "Test message to channel"
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    await update.message.reply_text("📢 Message sent to channel.")

async def send_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) or "Test message to group"
    await context.bot.send_message(chat_id=GROUP_ID, text=text)
    await update.message.reply_text("👥 Message sent to group.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

# --- Handlers ---
# Admin handlers
application.add_handler(CommandHandler("start", start, filters=filters.User(user_id=ADMIN_ID)))
application.add_handler(CommandHandler("channel", send_to_channel, filters=filters.User(user_id=ADMIN_ID)))
application.add_handler(CommandHandler("group", send_to_group, filters=filters.User(user_id=ADMIN_ID)))
application.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMIN_ID), echo))

# Catch-all for unauthorized users
application.add_handler(MessageHandler(filters.ALL & ~filters.User(user_id=ADMIN_ID), block_non_admin))

# --- Flask routes ---
@app.route("/")
def home():
    return "Bot is running on Render!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return {"ok": True}

# --- Entrypoint ---
if __name__ == "__main__":
    if os.getenv("RENDER"):
        print("🚀 Running with webhook on Render...")
    else:
        print("🤖 Running locally with polling...")
        application.run_polling()