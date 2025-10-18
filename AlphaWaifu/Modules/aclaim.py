# AlphaWaifu/Modules/aclaim.py

from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import (
    get_random_waifu,
    add_to_harem,
    RARITY_MAP,
    save_user,
    users_collection,
)


# -------------------- ACLAIM -------------------- #
async def aclaim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # ✅ Agar private chat hai to block karo
    if chat.type == "private":
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚀 Join Now", url="https://t.me/NARUTO_X_SUPPORT")]]
        )
        return await update.message.reply_text(
            "🎉𝐁𝐞𝐜𝐨𝐦𝐞 𝐚 𝐩𝐚𝐫𝐭 𝐨𝐟 𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐜𝐥𝐚𝐢𝐦 𝐲𝐨𝐮𝐫 𝐝𝐚𝐢𝐥𝐲 𝐜𝐡𝐚𝐫𝐚𝐜𝐭𝐞𝐫!🎁",
            reply_markup=keyboard
        )

    # ✅ Save user to DB
    await save_user(user.id, user.username, user.first_name)

    # 🔎 User ka last claim check karo
    user_data = await users_collection.find_one({"user_id": user.id})
    now = datetime.utcnow()

    if user_data and "last_aclaim" in user_data:
        last_claim = user_data["last_aclaim"]

        # Agar same din claim kiya tha to block
        if last_claim.date() == now.date():
            reset_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            remaining = reset_time - now
            hours, remainder = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            return await update.message.reply_text(
                f"⏳ You have already claimed today!\n"
                f"🕛 Next claim available in **{hours}h {minutes}m** (after midnight UTC)."
            )

    # 🎲 Random waifu select karo
    waifu = await get_random_waifu()
    if not waifu:
        return await update.message.reply_text("❌ No waifus available. Please upload first!")

    rarity_text = RARITY_MAP.get(waifu["rarity"], "❔ Unknown")

    # 🛠 Add to user harem
    await add_to_harem(
        user_id=user.id,
        waifu=waifu,
        chat_id=chat.id,
        first_name=user.first_name,
        username=user.username
    )

    # 📝 Stylish caption
    caption = (
        f"🎉 Congratulations {user.first_name}! 🎉\n\n"
        f"★ Name: {waifu['name']}\n"
        f"★ Rarity: {rarity_text}\n"
        f"★ Anime: {waifu['anime']}\n\n"
        f"✨ Come back for more luck tomorrow!"
    )

    # 📸 Send waifu image/video
    if waifu["media_type"] == "photo":
        await context.bot.send_photo(chat.id, waifu["file_id"], caption=caption)
    elif waifu["media_type"] == "video":
        await context.bot.send_video(chat.id, waifu["file_id"], caption=caption)
    else:
        await update.message.reply_text(caption)

    # ✅ Update last claim time
    await users_collection.update_one(
        {"user_id": user.id},
        {"$set": {"last_aclaim": now}},
        upsert=True
    )


# -------------------- REGISTER -------------------- #
def register(application: Application):
    application.add_handler(CommandHandler("aclaim", aclaim))