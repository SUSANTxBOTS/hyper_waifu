import random
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, Application
from AlphaWaifu.db import waifu_collection, RARITY_MAP
import AlphaWaifu.memory as memory   # ✅ direct import

# Track msg counts per chat
MESSAGE_COUNT = {}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Ignore bots
    if update.effective_user and update.effective_user.is_bot:
        return

    # Increase counter
    MESSAGE_COUNT[chat_id] = MESSAGE_COUNT.get(chat_id, 0) + 1

    # ✅ Read latest drop interval dynamically
    drop_interval = memory.DROP_INTERVAL

    # Check drop condition
    if MESSAGE_COUNT[chat_id] >= drop_interval:
        MESSAGE_COUNT[chat_id] = 0  # reset

        # Pick random waifu
        waifus = await waifu_collection.aggregate([{"$sample": {"size": 1}}]).to_list(1)
        if not waifus:
            return

        waifu = waifus[0]
        rarity_text = RARITY_MAP.get(waifu.get("rarity"), "Unknown")

        # Check file_id/media_type
        file_id = waifu.get("file_id")
        media_type = waifu.get("media_type")

        if not file_id or not media_type:
            await context.bot.send_message(chat_id, "⚠️ This waifu is missing media. Please re-upload.")
            return

        # ✅ Fixed caption with proper triple quotes and rarity_text
        caption = (
            f"⚡ ᴀ {rarity_text} ᴄʜᴀʀᴀᴄᴛᴇʀ ᴀᴘᴘᴇᴀʀs! ⚡\n"
            f"🔍 ᴜsᴇ /guess ᴛᴏ ᴄʟᴀɪᴍ ᴛʜɪs ᴍʏsᴛᴇʀɪᴏᴜs ᴄʜᴀʀᴀᴄᴛᴇʀ!\n"
            f"🌟 ʜᴜʀʀʏ ʙᴇғᴏʀᴇ sᴏᴍᴇᴏɴᴇ ᴇʟsᴇ ᴄʟᴀɪᴍs ɪᴛ!"
        )

        # Send drop
        if media_type == "photo":
            msg = await context.bot.send_photo(chat_id, photo=file_id, caption=caption)
        elif media_type == "video":
            msg = await context.bot.send_video(chat_id, video=file_id, caption=caption)
        else:
            await context.bot.send_message(chat_id, "⚠️ Unsupported media type.")
            return

        # Save drop in memory
        memory.CURRENT_DROPS[chat_id] = {
            "waifu_id": waifu["waifu_id"],
            "name": waifu["name"],
            "anime": waifu["anime"],
            "rarity": waifu["rarity"],
            "file_id": file_id,
            "media_type": media_type,
            "message_id": msg.message_id,
        }


def register(application: Application):
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))