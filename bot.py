import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Use environment variable with fallback for local testing
TOKEN =('')

# Store admin IDs for private chat verification or fallback
ADMIN_IDS = {6952136450}  # Admin ID provided

async def is_admin(update):
    """Check if the user is an admin in the chat."""
    try:
        if update.message.chat.type in ['group', 'supergroup']:
            admins = await update.message.chat.get_administrators()
            admin_ids = {admin.user.id for admin in admins}
            return update.message.from_user.id in admin_ids
        return update.message.from_user.id in ADMIN_IDS
    except TelegramError as e:
        logger.error(f"Error checking admin status: {e}")
        return False

async def start(update, context):
    """Admin-only welcome message."""
    if await is_admin(update):
        try:
            welcome_text = "Hello! I’m your admin-only bot. Use /help for commands."
            await update.message.reply_text(welcome_text)
        except TelegramError as e:
            logger.error(f"Error in /start: {e}")
            await update.message.reply_text("An error occurred. Please try again later.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def help_command(update, context):
    """Admin-only help message."""
    if await is_admin(update):
        try:
            help_text = """🤖 Admin-Only Bot Commands:
- /start - Start the bot and get a welcome message
- /help - Show this help menu
- /ping - Check if the bot is alive
- /echo <text> - Echo back the text you send
- /admin <message> - Send a message to admins
- /kick @username - Kick a user from the group
- /mute @username - Mute a user in the group

⚠️ Note: All commands are restricted to admins."""
            await update.message.reply_text(help_text)
        except TelegramError as e:
            logger.error(f"Error in /help: {e}")
            await update.message.reply_text("An error occurred. Please try again later.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def ping(update, context):
    """Admin-only ping response."""
    if await is_admin(update):
        try:
            await update.message.reply_text("Pong! 👾")
        except TelegramError as e:
            logger.error(f"Error in /ping: {e}")
            await update.message.reply_text("An error occurred. Please try again later.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def echo(update, context):
    """Admin-only echo command."""
    if await is_admin(update):
        try:
            if context.args:
                await update.message.reply_text(" ".join(context.args))
            else:
                await update.message.reply_text("Please provide some text to echo!")
        except TelegramError as e:
            logger.error(f"Error in /echo: {e}")
            await update.message.reply_text("An error occurred. Please try again later.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def admin_message(update, context):
    """Admin-only command to send messages to the chat."""
    if await is_admin(update):
        try:
            if context.args:
                message = " ".join(context.args)
                chat_id = update.message.chat_id
                await context.bot.send_message(chat_id=chat_id, text=f"Admin broadcast: {message}")
                await update.message.reply_text("Message broadcasted to the chat!")
            else:
                await update.message.reply_text("Usage: /admin <message>")
        except TelegramError as e:
            logger.error(f"Error in /admin: {e}")
            await update.message.reply_text("An error occurred. Please try again later.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def kick(update, context):
    """Admin-only command to kick a user."""
    if await is_admin(update):
        try:
            if len(context.args) > 0 and context.args[0].startswith('@'):
                username = context.args[0][1:]  # Remove @ symbol
                member = await context.bot.get_chat_member(update.message.chat_id, username)
                await context.bot.kick_chat_member(update.message.chat_id, member.user.id)
                await context.bot.unban_chat_member(update.message.chat_id, member.user.id)  # Unban to allow rejoin
                await update.message.reply_text(f"Kicked {context.args[0]}!")
            else:
                await update.message.reply_text("Usage: /kick @username")
        except TelegramError as e:
            logger.error(f"Error in /kick: {e}")
            await update.message.reply_text("Failed to kick user. Check permissions or username.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def mute(update, context):
    """Admin-only command to mute a user."""
    if await is_admin(update):
        try:
            if len(context.args) > 0 and context.args[0].startswith('@'):
                username = context.args[0][1:]  # Remove @ symbol
                member = await context.bot.get_chat_member(update.message.chat_id, username)
                await context.bot.restrict_chat_member(
                    chat_id=update.message.chat_id,
                    user_id=member.user.id,
                    permissions=None,  # Revoke all permissions (mute)
                    until_date=None  # Indefinite mute
                )
                await update.message.reply_text(f"Muted {context.args[0]}!")
            else:
                await update.message.reply_text("Usage: /mute @username")
        except TelegramError as e:
            logger.error(f"Error in /mute: {e}")
            await update.message.reply_text("Failed to mute user. Check permissions or username.")
    else:
        await update.message.reply_text("Only admins can use this command.")

async def handle_message(update, context):
    """Respond to non-command messages (admin-only)."""
    if await is_admin(update):
        try:
            await update.message.reply_text("I received your message! Use /help for commands.")
        except TelegramError as e:
            logger.error(f"Error in message handler: {e}")
    else:
        await update.message.reply_text("Only admins can interact with this bot.")

async def error_handler(update, context):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")

async def main():
    """Start the bot."""
    logger.info("Bot is starting... at 10:33 PM WAT, August 13, 2025")
    try:
        # Initialize the application
        app = Application.builder().token(TOKEN).build()

        # Add command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("ping", ping))
        app.add_handler(CommandHandler("echo", echo))
        app.add_handler(CommandHandler("admin", admin_message))
        app.add_handler(CommandHandler("kick", kick))
        app.add_handler(CommandHandler("mute", mute))

        # Add message handler for non-command messages
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Add error handler
        app.add_error_handler(error_handler)

        # Initialize, start, and begin polling
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        logger.info("Bot is running...")
        await asyncio.Event().wait()  # Keep bot running
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Bot shutting down...")
        await app.stop()

if __name__ == '__main__':
    asyncio.run(main())