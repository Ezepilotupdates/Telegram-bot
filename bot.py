import os
from flask import Flask, request
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6952136450"))   # admin
GROUP_ID = int(os.getenv("GROUP_ID", "-1002493478840"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002845832658"))

# Flask app
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(TOKEN).build()

# Restrict to admin
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ You are not authorized to use this bot.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# Helper → notify admin privately
async def log_action(action: str, user_id: int, user_name: str = ""):
    msg = f"📢 *Action:* {action}\n👤 *User:* {user_name} (`{user_id}`)"
    await application.bot.send_message(
        chat_id=ADMIN_ID,
        text=msg,
        parse_mode="Markdown"
    )

# /start
@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ Bot is active.\n\n"
        f"Group ID: {GROUP_ID}\n"
        f"Channel ID: {CHANNEL_ID}"
    )

# --- Messaging Commands ---
@admin_only
async def send_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /sendgroup <message>")
        return
    message = " ".join(context.args)
    await application.bot.send_message(chat_id=GROUP_ID, text=message)
    await update.message.reply_text("✅ Sent to group.")

@admin_only
async def send_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /sendchannel <message>")
        return
    message = " ".join(context.args)
    await application.bot.send_message(chat_id=CHANNEL_ID, text=message)
    await update.message.reply_text("✅ Sent to channel.")

@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    await application.bot.send_message(chat_id=GROUP_ID, text=message)
    await application.bot.send_message(chat_id=CHANNEL_ID, text=message)
    await update.message.reply_text("✅ Broadcast sent to group and channel.")

# --- Moderation Commands ---
@admin_only
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user’s message with /ban to ban them.")
        return
    user = update.message.reply_to_message.from_user
    await application.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user.id)
    await update.message.reply_text(f"🚫 {user.first_name} banned.")
    await log_action("Ban", user.id, user.first_name)

@admin_only
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user’s message with /kick to kick them.")
        return
    user = update.message.reply_to_message.from_user
    await application.bot.ban_chat_member(chat_id=GROUP_ID, user_id=user.id)
    await application.bot.unban_chat_member(chat_id=GROUP_ID, user_id=user.id)
    await update.message.reply_text(f"👢 {user.first_name} kicked.")
    await log_action("Kick", user.id, user.first_name)

@admin_only
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user’s message with /mute to mute them.")
        return
    user = update.message.reply_to_message.from_user
    await application.bot.restrict_chat_member(
        chat_id=GROUP_ID,
        user_id=user.id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text(f"🔇 {user.first_name} muted.")
    await log_action("Mute", user.id, user.first_name)

@admin_only
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a user’s message with /unmute to restore permissions.")
        return
    user = update.message.reply_to_message.from_user
    await application.bot.restrict_chat_member(
        chat_id=GROUP_ID,
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await update.message.reply_text(f"🔊 {user.first_name} unmuted.")
    await log_action("Unmute", user.id, user.first_name)

# --- Register commands ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("sendgroup", send_group))
application.add_handler(CommandHandler("sendchannel", send_channel))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("ban", ban))
application.add_handler(CommandHandler("kick", kick))
application.add_handler(CommandHandler("mute", mute))
application.add_handler(CommandHandler("unmute", unmute))

# Webhook for Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)