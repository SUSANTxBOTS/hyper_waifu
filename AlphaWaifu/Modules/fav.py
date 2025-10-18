from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo
)
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application
from AlphaWaifu.db import users_collection, waifu_collection, RARITY_MAP


# ---------- /FAV COMMAND ---------- #
async def fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if len(context.args) < 1:
        return await update.message.reply_text("❌ Usage: /fav <waifu_id>")

    waifu_id = context.args[0]
    waifu = await waifu_collection.find_one({"waifu_id": waifu_id})

    if not waifu:
        return await update.message.reply_text("❌ Waifu not found.")

    rarity_text = RARITY_MAP.get(waifu["rarity"], "❔ Unknown")

    caption = (
        "💎 Confirm Your Choice! 💎\n\n"
        f"🎭 Name: {waifu['name']}\n"
        f"⛩️ Anime: {waifu['anime']}\n"
        f"🪄 Rarity: {rarity_text}\n\n"
        f"⚡ Are you ready to set {waifu['name']} as your favorite?\n"
        "Choose an option below:"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"fav_confirm_{waifu_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="fav_cancel"),
        ]
    ]

    if waifu["media_type"] == "photo":
        await context.bot.send_photo(
            update.effective_chat.id,
            waifu["file_id"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif waifu["media_type"] == "video":
        await context.bot.send_video(
            update.effective_chat.id,
            waifu["file_id"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    else:
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard))


# ---------- CALLBACK HANDLER ---------- #
async def fav_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    data = query.data
    if data.startswith("fav_confirm_"):
        waifu_id = data.split("_")[2]
        waifu = await waifu_collection.find_one({"waifu_id": waifu_id})
        if not waifu:
            return await query.edit_message_text("❌ Waifu not found.")

        # ✅ Save to DB
        await users_collection.update_one(
            {"user_id": user.id},
            {"$set": {"fav_waifu_id": waifu_id}},
            upsert=True,
        )

        rarity_text = RARITY_MAP.get(waifu["rarity"], "❔ Unknown")
        caption = (
            f"🌟 Success! {waifu['name']} is now your favorite character! ✅\n\n"
            f"🎭 Name: {waifu['name']}\n"
            f"⛩️ Anime: {waifu['anime']}\n"
            f"🪄 Rarity: {rarity_text}\n\n"
            f"Enjoy your journey with {waifu['name']}!"
        )

        if waifu["media_type"] == "photo":
            await query.edit_message_media(
                media=InputMediaPhoto(waifu["file_id"], caption=caption),
            )
        elif waifu["media_type"] == "video":
            await query.edit_message_media(
                media=InputMediaVideo(waifu["file_id"], caption=caption),
            )
        else:
            await query.edit_message_text(caption)

    elif data == "fav_cancel":
        await query.edit_message_text("❌ Favourite selection cancelled.")


# ---------- REGISTER ---------- #
def register(application: Application):
    application.add_handler(CommandHandler("fav", fav))
    application.add_handler(CallbackQueryHandler(fav_callback, pattern="^fav_"))