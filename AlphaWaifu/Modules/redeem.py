from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import redeem_codes_collection, add_to_harem, RARITY_MAP


# -------------------- REDEEM -------------------- #
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if len(context.args) < 1:
        return await update.message.reply_text("❌ Usage: /redeem <code>")

    code = context.args[0].strip().lower()

    # ✅ Find code
    code_data = await redeem_codes_collection.find_one({"code": code})
    if not code_data:
        return await update.message.reply_text("❌ Invalid or expired code!")

    if code_data["remaining"] <= 0:
        return await update.message.reply_text("❌ This code has expired!")

    # ✅ Check if user already redeemed
    redeemed_users = code_data.get("redeemed_users", [])
    if user.id in redeemed_users:
        return await update.message.reply_text("❌ You have already redeemed this code!")

    waifu = code_data["waifu"]
    rarity_text = RARITY_MAP.get(waifu["rarity"], "❔ Unknown")

    # Add waifu to user's harem
    await add_to_harem(
        user_id=user.id,
        waifu=waifu,
        chat_id=chat.id,
        first_name=user.first_name,
        username=user.username,
    )

    # Decrease remaining and add user to redeemed_users
    await redeem_codes_collection.update_one(
        {"code": code},
        {"$inc": {"remaining": -1}, "$push": {"redeemed_users": user.id}}
    )

    # Get updated remaining
    updated = await redeem_codes_collection.find_one({"code": code})
    remaining = updated["remaining"]

    # ✅ Fancy Caption
    caption = (
        "✨ 𝗥𝗘𝗗𝗘𝗘𝗠 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟! ✨\n\n"
        f"🎉 {user.mention_html()} you have claimed:\n\n"
        f"📛 Name: {waifu['name']}\n"
        f"🎬 Anime: {waifu['anime']}\n"
        f"🏷️ Rarity: {rarity_text}\n"
        f"🎟️ Remaining: {remaining}\n"
    )

    if waifu["media_type"] == "photo":
        await context.bot.send_photo(chat.id, waifu["file_id"], caption=caption, parse_mode="HTML")
    elif waifu["media_type"] == "video":
        await context.bot.send_video(chat.id, waifu["file_id"], caption=caption, parse_mode="HTML")
    else:
        await update.message.reply_text(caption, parse_mode="HTML")


def register(application: Application):
    application.add_handler(CommandHandler("redeem", redeem))