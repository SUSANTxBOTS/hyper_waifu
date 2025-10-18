from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import waifu_collection, RARITY_MAP, uploaders_collection
from AlphaWaifu.config import SUDO_USERS, CHARA_CHANNEL_ID


# -------------------- CHECK IF USER CAN UPLOAD -------------------- #
async def is_uploader(user_id: int) -> bool:
    if user_id in SUDO_USERS:
        return True  # root SUDO can always upload
    check = await uploaders_collection.find_one({"user_id": user_id})
    return bool(check)


# -------------------- GET NEXT ID -------------------- #
async def get_next_waifu_id() -> str:
    last = await waifu_collection.find().sort("waifu_id", -1).to_list(1)
    last_id = int(last[0]["waifu_id"]) if last else 0
    return str(last_id + 1).zfill(2)


# -------------------- UPLOAD -------------------- #
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await is_uploader(user.id):
        return await update.message.reply_text("❌ You are not authorized to use this command.")

    if len(context.args) < 3:
        return await update.message.reply_text(
            "❌ Usage: /upload <name> <anime> <rarity_id>\n"
            "👉 Example: /upload Naruto-Uzumaki Naruto-Shippuden 10\n\n"
            "💡 Tip: Reply to an image/video with this command!"
        )

    # ✅ pehle character name, fir anime name
    name = context.args[0].replace("-", " ")
    anime = context.args[1].replace("-", " ")

    try:
        rarity_id = int(context.args[2])
    except ValueError:
        return await update.message.reply_text("❌ Rarity ID must be a number.")

    if rarity_id not in RARITY_MAP:
        return await update.message.reply_text("❌ Invalid rarity ID. Please check RARITY_MAP.")

    rarity_text = RARITY_MAP[rarity_id]

    media_type, media_file_id = None, None
    if update.message.photo:
        media_type, media_file_id = "photo", update.message.photo[-1].file_id
    elif update.message.video:
        media_type, media_file_id = "video", update.message.video.file_id
    elif update.message.reply_to_message:
        if update.message.reply_to_message.photo:
            media_type, media_file_id = "photo", update.message.reply_to_message.photo[-1].file_id
        elif update.message.reply_to_message.video:
            media_type, media_file_id = "video", update.message.reply_to_message.video.file_id

    if not media_file_id:
        return await update.message.reply_text("❌ Please attach or reply to a photo/video with the /upload command.")

    waifu_id = await get_next_waifu_id()

    waifu_data = {
        "waifu_id": waifu_id,
        "name": name,
        "anime": anime,
        "rarity": rarity_id,
        "media_type": media_type,
        "file_id": media_file_id,
        "added_by": user.first_name,
        "added_id": user.id,
    }
    await waifu_collection.insert_one(waifu_data)

    # Caption (plain text - safe)
    caption = (
        "✨ New Waifu Added! ✨\n\n"
        f"👩‍🎤 Character Name: {name}\n"
        f"📺 Anime Name: {anime}\n"
        f"🌟 Rarity: {rarity_text}\n"
        f"🆔 ID: {waifu_id}\n"
        f"➕ Added by: {user.first_name}"
    )

    if media_type == "photo":
        await context.bot.send_photo(CHARA_CHANNEL_ID, photo=media_file_id, caption=caption)
    elif media_type == "video":
        await context.bot.send_video(CHARA_CHANNEL_ID, video=media_file_id, caption=caption)

    await update.message.reply_text(
        f"✅ Waifu {waifu_id} uploaded successfully and posted in channel!"
    )


# -------------------- REGISTER HANDLER -------------------- #
def register(application: Application):
    application.add_handler(CommandHandler("upload", upload))