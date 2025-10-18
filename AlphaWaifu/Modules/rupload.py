import random, string
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import redeem_codes_collection, RARITY_MAP, get_next_global_waifu_id
from AlphaWaifu.config import SUDO_USERS, CHARA_CHANNEL_ID


# -------------------- RANDOM CODE GENERATOR -------------------- #
def generate_code():
    return "alpha" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


# -------------------- UPLOAD WITH CODE -------------------- #
async def rupload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in SUDO_USERS:
        return await update.message.reply_text("❌ You are not authorized to use this command.")

    if len(context.args) < 4:
        return await update.message.reply_text(
            "❌ Usage: /rupload <name> <anime> <rarity_id> <quantity>\n"
            "👉 Example: /rupload Naruto-Uzumaki Naruto-Shippuden 10 5\n\n"
            "💡 Tip: Reply to an image/video with this command!"
        )

    name = context.args[0].replace("-", " ")
    anime = context.args[1].replace("-", " ")

    try:
        rarity_id = int(context.args[2])
        quantity = int(context.args[3])
    except ValueError:
        return await update.message.reply_text("❌ Rarity ID and Quantity must be numbers.")

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
        return await update.message.reply_text("❌ Please attach or reply to a photo/video with the /rupload command.")

    waifu_id = await get_next_global_waifu_id()
    redeem_code = generate_code()

    # ✅ Save redeem code
    code_data = {
        "code": redeem_code,
        "waifu": {
            "waifu_id": waifu_id,
            "name": name,
            "anime": anime,
            "rarity": rarity_id,
            "media_type": media_type,
            "file_id": media_file_id,
        },
        "quantity": quantity,
        "remaining": quantity,
        "created_by": user.id,
    }
    await redeem_codes_collection.insert_one(code_data)

    # ✅ Drop Alert to Channel
    drop_caption = (
        "┏━━━━━━━━━━━━━━━━━┓\n"
        "💗 𝗪𝗮𝗶𝗳𝘂 𝗗𝗿𝗼𝗽 𝗔𝗹𝗲𝗿𝘁 💗\n"
        "┗━━━━━━━━━━━━━━━━━┛\n\n"
        f"👑 𝗡𝗮𝗺𝗲: {name}\n"
        f"🔮 𝗥𝗮𝗿𝗶𝘁𝘆: {rarity_text}\n"
        f"🎯 𝗤𝘂𝗮𝗻𝘁𝗶𝘁𝘆: {quantity} only\n\n"
        f"💌 𝗥𝗲𝗱𝗲𝗲𝗺: `/redeem {redeem_code}`\n\n"
        "⚡ First come, first serve!\n"
        "Once she’s gone… she’s gone 💨"
    )

    if media_type == "photo":
        await context.bot.send_photo(CHARA_CHANNEL_ID, media_file_id, caption=drop_caption, parse_mode="Markdown")
    elif media_type == "video":
        await context.bot.send_video(CHARA_CHANNEL_ID, media_file_id, caption=drop_caption, parse_mode="Markdown")
    else:
        await context.bot.send_message(CHARA_CHANNEL_ID, drop_caption, parse_mode="Markdown")

    # ✅ Confirm to uploader
    await update.message.reply_text(
        f"✅ Redeem Code Generated!\n\n"
        f"👩‍🎤 Name: {name}\n"
        f"📺 Anime: {anime}\n"
        f"🌟 Rarity: {rarity_text}\n"
        f"🆔 ID: {waifu_id}\n"
        f"🎟 Code: `{redeem_code}`\n"
        f"🔢 Quantity: {quantity}\n\n"
        f"💠 Added by: {user.first_name}"
    )


def register(application: Application):
    application.add_handler(CommandHandler("rupload", rupload))