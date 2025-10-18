import re
import time
import random
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import (
    add_to_harem, update_coins, get_coins,
    add_guess,  # ✅ save guess
    RARITY_MAP
)
from AlphaWaifu.memory import CURRENT_DROPS

# Track drop timestamps for time calculation
DROP_TIMESTAMPS = {}   # {chat_id: drop_time}

# 🎭 Reaction emojis
REACTIONS = ["🔥", "😲", "💯", "🥵", "🫡", "😎", "🎯", "👏", "😳", "🤟",
             "🤩", "😊", "🥳", "😍", "🤯", "😈", "😘", "😇", "🤑", "🎉"]


async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    args = context.args

    # ✅ Check if there’s an active drop
    if chat_id not in CURRENT_DROPS:
        return await update.message.reply_text(
            "❌ No active drop! Wait for the next one."
        )

    waifu = CURRENT_DROPS[chat_id]

    # ✅ Check if already guessed
    if waifu.get("captured_by"):
        return await update.message.reply_text(
            "❌ Already guessed by someone.. Try next time!"
        )

    # ✅ If no args
    if not args:
        return await update.message.reply_text(
            "❌ Please provide the character name.\nUsage: `/guess Naruto`",
            parse_mode="Markdown"
        )

    guess_text = " ".join(args).lower()

    # ✅ Prepare correct answer text
    correct_name = waifu["name"].lower()
    correct_anime = waifu["anime"].lower()

    # ✅ Matching (loose check)
    if (
        re.search(rf"\b{re.escape(guess_text)}\b", correct_name)
        or guess_text in correct_name
        or guess_text in correct_anime
    ):
        # ✅ Correct guess
        waifu["captured_by"] = user.id  # lock this drop

        # Add to DB harem
        await add_to_harem(
            user_id=user.id,
            waifu=waifu,
            chat_id=chat_id,
            first_name=user.first_name,
            username=user.username
        )

        # Save guess history ✅
        await add_guess(
            user_id=user.id,
            chat_id=chat_id,
            waifu_id=waifu["waifu_id"],  # 🆕 waifu_id track
            first_name=user.first_name,
            username=user.username
        )

        # Add coins
        reward = 100  # 👈 coins tu customize kar sakta hai
        await update_coins(user.id, reward)
        balance = await get_coins(user.id)

        # Random reaction emoji 🎭
        reaction = random.choice(REACTIONS)

        # ✅ Msg1: Coins info (reaction added)
        await update.message.reply_text(
            f"{reaction} 🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!\n\n"
            f"💰 ʏᴏᴜ ᴇᴀʀɴᴇᴅ +{reward} ᴄᴏɪɴs ғᴏʀ ɢᴜᴇssɪɴɢ ᴄᴏʀʀᴇᴄᴛʟʏ!\n\n"
            f"🏦 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ ➜ {balance} ᴄᴏɪɴs"
        )

        # ✅ Msg2: Capture info
        rarity_text = RARITY_MAP.get(waifu["rarity"], "Unknown")
        await update.message.reply_text(
            f"🌟 {user.first_name}, ʏᴏᴜ’ᴠᴇ ᴄᴀᴘᴛᴜʀᴇᴅ ᴀ ɴᴇᴡ ᴡᴀɪғᴜ! 🎊\n\n"
            f"⛩️ 𝗡𝗔𝗠𝗘 ➜ {waifu['name']}\n"
            f"🍁 𝗔𝗡𝗜𝗠𝗘 ➜ {waifu['anime']}\n"
            f"✨ 𝗥𝗔𝗥𝗜𝗧𝗬 ➜ {rarity_text}\n\n"
            f"💕 ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ʜᴀʀᴇᴍ!\n"
            f"📖 ᴄʜᴇᴄᴋ ɪᴛ ᴜsɪɴɢ ➜ /harem"
        )

        # Clear drop
        CURRENT_DROPS.pop(chat_id, None)
        DROP_TIMESTAMPS.pop(chat_id, None)

    else:
        # ❌ Wrong guess
        await update.message.reply_text("❌ Wrong guess! Try again...")


def register(application: Application):
    application.add_handler(CommandHandler("guess", guess))