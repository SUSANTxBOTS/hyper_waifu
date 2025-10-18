import random
import string
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import redeem_codes_collection, users_collection
from AlphaWaifu.config import SUDO_USERS, CHARA_CHANNEL_ID

# -------------------- CUPlOAD -------------------- #
async def cupload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ You are not allowed to use this command!")

    if len(context.args) < 2:
        return await update.message.reply_text("❌ Usage: /cupload <coins> <quantity>")

    coins = int(context.args[0])
    quantity = int(context.args[1])

    # Generate ONE code for the giveaway
    code = "alpha" + "".join(random.choices(string.ascii_lowercase + string.digits, k=5))

    # Insert code into DB with quantity
    await redeem_codes_collection.insert_one({
        "code": code,
        "coins": coins,
        "remaining": quantity,  # how many users can redeem
        "redeemed_users": []
    })

    # Send ONE giveaway message to channel
    caption = (
        "┏━━━━━━━━━━━━━━┓\n"
        "💰 𝐂𝐎𝐈𝐍 𝐒𝐓𝐎𝐑𝐌 💰\n"
        "┗━━━━━━━━━━━━━━┛\n\n"
        f"💎 𝐏𝐫𝐢𝐳𝐞: {coins:,} Coins 🪙\n"
        f"📦 𝐒𝐥𝐨𝐭𝐬: Only {quantity} Lucky Winners 🎯\n\n"
        "💌 𝐂𝐥𝐚𝐢𝐦 𝐍𝐨𝐰:\n"
        f"/credeem {code}\n"
        "⚡ Blink and it’s gone — move faster than Minato! 🚀"
    )
    await context.bot.send_message(chat_id=CHARA_CHANNEL_ID, text=caption)

    await update.message.reply_text(f"✅ Giveaway created! Code: {code} | Quantity: {quantity}")


# -------------------- CREDEEM -------------------- #
async def credeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if len(context.args) < 1:
        return await update.message.reply_text("❌ Usage: /credeem <code>")

    code = context.args[0].strip().lower()
    code_data = await redeem_codes_collection.find_one({"code": code})

    if not code_data:
        return await update.message.reply_text("❌ Invalid or expired code!")

    if code_data["remaining"] <= 0:
        return await update.message.reply_text("❌ This code has already been fully claimed!")

    if user.id in code_data.get("redeemed_users", []):
        return await update.message.reply_text("❌ You have already redeemed this code!")

    coins = code_data["coins"]

    # Add coins to user
    await users_collection.update_one(
        {"user_id": user.id},
        {"$inc": {"coins": coins}},
        upsert=True
    )

    # Update code document
    await redeem_codes_collection.update_one(
        {"code": code},
        {"$inc": {"remaining": -1}, "$push": {"redeemed_users": user.id}}
    )

    await update.message.reply_text(f"✅ {coins:,} coins successfully redeemed!")


# -------------------- REGISTER -------------------- #
def register(application: Application):
    application.add_handler(CommandHandler("cupload", cupload))
    application.add_handler(CommandHandler("credeem", credeem))