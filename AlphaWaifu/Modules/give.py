# AlphaWaifu/Modules/give.py

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import update_coins, users_collection, save_user, get_coins


# -------------------- GIVE -------------------- #
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user

    # ✅ Sender ka balance check karo
    sender_balance = await get_coins(sender.id)

    # Agar reply hai aur amount diya gaya
    if update.message.reply_to_message and len(context.args) == 1:
        try:
            amount = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("⚠️ Invalid amount!")

        if amount <= 0:
            return await update.message.reply_text("❌ Amount must be greater than 0!")

        # Balance check
        if sender_balance < amount:
            return await update.message.reply_text("💔 You don’t have enough coins!")

        target = update.message.reply_to_message.from_user
        await save_user(target.id, target.username, target.first_name)

        # Coins transfer
        await update_coins(sender.id, -amount)   # sender se hatao
        await update_coins(target.id, amount)   # target ko do

        return await update.message.reply_text(
            f"💸 **{amount} Coins Transferred!**\n\n"
            f"👤 From: [{sender.first_name}](tg://user?id={sender.id})\n"
            f"➡️ To: [{target.first_name}](tg://user?id={target.id})",
            parse_mode="Markdown"
        )

    # Agar username/user_id + amount diya gaya
    elif len(context.args) == 2:
        user_arg = context.args[0]
        try:
            amount = int(context.args[1])
        except ValueError:
            return await update.message.reply_text("⚠️ Invalid amount!")

        if amount <= 0:
            return await update.message.reply_text("❌ Amount must be greater than 0!")

        # Balance check
        if sender_balance < amount:
            return await update.message.reply_text("💔 You don’t have enough coins!")

        # Target user dhundo
        target = None
        if user_arg.startswith("@"):
            target = await users_collection.find_one({"username": user_arg[1:]})
        elif user_arg.isdigit():
            target = await users_collection.find_one({"user_id": int(user_arg)})

        if not target:
            return await update.message.reply_text("❌ User not found in database!")

        # Coins transfer
        await update_coins(sender.id, -amount)    # sender se hatao
        await update_coins(target["user_id"], amount)  # target ko do

        return await update.message.reply_text(
            f"💸 **{amount} Coins Transferred!**\n\n"
            f"👤 From: [{sender.first_name}](tg://user?id={sender.id})\n"
            f"➡️ To: [{target.get('first_name', 'Unknown')}](tg://user?id={target['user_id']})",
            parse_mode="Markdown"
        )

    else:
        return await update.message.reply_text(
            "⚡ Correct Usage:\n\n"
            "👉 Reply: `/give 100`\n"
            "👉 Username/ID: `/give @username 100` or `/give 12345678 100`",
            parse_mode="Markdown"
        )


# -------------------- REGISTER -------------------- #
def register(application: Application):
    application.add_handler(CommandHandler("give", give))