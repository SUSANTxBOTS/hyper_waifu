# AlphaWaifu/Modules/reset.py

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import (
    users_collection,
    groups_collection,
    waifu_collection,
    guesses_collection,
    settings_collection,
)
from AlphaWaifu.config import SUDO_USERS


# 🔥 Reset ALL Data (Global)
async def reset_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ✅ Sirf SUDO_USERS ko allow karo
    if user.id not in SUDO_USERS:
        return await context.bot.send_message(chat_id, "❌ You are not authorized to use this command.")

    # 🔥 Drop all collections
    await users_collection.drop()
    await groups_collection.drop()
    await waifu_collection.drop()
    await guesses_collection.drop()
    await settings_collection.drop()

    await context.bot.send_message(
        chat_id,
        "⚠️ **All Data Has Been Reset!** ⚠️\n\n"
        "🧹 Users, Groups, Waifus, Guesses, Coins, Tokens sab delete kar diye gaye.",
        parse_mode="Markdown"
    )


# 🔥 Reset ONE User Data
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    # ✅ Sirf SUDO_USERS ko allow karo
    if user.id not in SUDO_USERS:
        return await context.bot.send_message(chat_id, "❌ You are not authorized to use this command.")

    if len(context.args) < 1:
        return await context.bot.send_message(chat_id, "⚠️ Usage: `/reset <user_id or @username>`", parse_mode="Markdown")

    target = context.args[0]

    # Agar username diya hai to user_id nikaalne ki try karo
    if target.startswith("@"):
        try:
            target_user = await context.bot.get_chat(target)
            target_id = target_user.id
        except Exception:
            return await context.bot.send_message(chat_id, f"❌ User {target} not found.")
    else:
        try:
            target_id = int(target)
        except ValueError:
            return await context.bot.send_message(chat_id, "⚠️ Invalid user_id or username.")

    # 🔥 User ka saara data delete karo
    await users_collection.delete_one({"user_id": target_id})
    await waifu_collection.delete_many({"owner_id": target_id})
    await guesses_collection.delete_many({"user_id": target_id})

    await context.bot.send_message(
        chat_id,
        f"🧹 **User Data Reset Successfully!**\n\n"
        f"👤 User ID: `{target_id}`\n"
        f"📦 Users, Waifus, Guesses, Coins, Tokens sab delete kar diye gaye.",
        parse_mode="Markdown"
    )


# 🔗 Register both commands
def register(application: Application):
    application.add_handler(CommandHandler("reset_all", reset_all))
    application.add_handler(CommandHandler("reset", reset))