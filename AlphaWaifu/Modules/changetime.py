from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.config import SUDO_USERS
from AlphaWaifu.memory import DROP_INTERVAL

async def changetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ You are not authorized to use this command.")

    if not context.args:
        return await update.message.reply_text(f"⚡ Current drop interval: {DROP_INTERVAL} messages\nUsage: /changetime <number>")

    try:
        new_time = int(context.args[0])
        if new_time < 1:
            raise ValueError
    except ValueError:
        return await update.message.reply_text("❌ Invalid number. Please enter a positive integer.")

    import AlphaWaifu.memory as memory
    memory.DROP_INTERVAL = new_time
    await update.message.reply_text(f"✅ Drop interval updated globally to {new_time} messages.")

def register(application: Application):
    application.add_handler(CommandHandler("changetime", changetime))