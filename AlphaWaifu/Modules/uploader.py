from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.config import SUDO_USERS
from AlphaWaifu.db import uploaders_collection


# -------------------- ADD SUDO (Uploader) -------------------- #
async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ You are not authorized to promote uploaders.")

    if not context.args:
        return await update.message.reply_text("❌ Usage: /addsudo <user_id>")

    try:
        new_id = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("❌ User ID must be a number.")

    existing = await uploaders_collection.find_one({"user_id": new_id})
    if existing:
        return await update.message.reply_text("⚠️ This user is already an uploader.")

    await uploaders_collection.insert_one({"user_id": new_id})

    await update.message.reply_text(
        f"✅ User `{new_id}` has been promoted as an uploader!",
        parse_mode="Markdown"
    )


# -------------------- REGISTER HANDLER -------------------- #
def register(application: Application):
    application.add_handler(CommandHandler("addsudo", add_sudo))