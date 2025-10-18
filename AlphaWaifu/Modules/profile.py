from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import users_collection, waifu_collection, get_coins, RARITY_MAP


def generate_progress_bar(progress: float, length: int = 18) -> str:
    """Fancy progress bar with %"""
    filled = int(length * progress)
    empty = length - filled
    return f"[{'▰' * filled}{'▱' * empty}] {progress * 100:.1f}%"


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Fetch user data
    user_data = await users_collection.find_one({"user_id": user_id}) or {}
    coins = user_data.get("coins", 0)
    harem = user_data.get("harem", [])

    guesses = len(harem)   # total collected by this user
    uploaded = await waifu_collection.count_documents({})  # total uploaded characters in DB
    progress = min(guesses / uploaded, 1.0) if uploaded > 0 else 0

    # rarity counts
    rarity_counts = {r: 0 for r in RARITY_MAP.values()}
    for w in harem:
        rarity_text = RARITY_MAP.get(w["rarity"], "❓ Unknown")
        rarity_counts[rarity_text] = rarity_counts.get(rarity_text, 0) + 1

    rarity_text_lines = "\n".join(
        f"  ❍ {rar} ➥ {count}" for rar, count in rarity_counts.items()
    )

    # Global rank (based on coins)
    total_users = await users_collection.count_documents({})
    higher_rank = await users_collection.count_documents({"coins": {"$gt": coins}})
    rank = higher_rank + 1 if total_users > 0 else 1

    profile_text = f"""
❖ 『{user.first_name}』 ɪɴғᴏʀᴍᴀᴛɪᴏɴ ❖
━━━━━━━━━━━━━━━━━━━━━
⬤ ᴜsᴇʀ ɪᴅ ➥ {user_id}
⬤ ᴍᴇɴᴛɪᴏɴ ➥ {user.mention_html()}
⬤ ᴄᴏɪɴ ➥ {coins}
⬤ ɢʟᴏʙᴀʟ ʀᴀɴᴋ ➥ #{rank}/{total_users}
⬤ ᴄʜᴀʀᴀᴄᴛᴇʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ➥ {guesses}/{uploaded}
⬤ ᴘʀᴏɢʀᴇss ʙᴀʀ ➥ {generate_progress_bar(progress)}
⬤ ʀᴀʀɪᴛʏ ᴄᴏᴜɴᴛ ➥
{rarity_text_lines}
━━━━━━━━━━━━━━━━━━━━━
"""

    await update.message.reply_text(profile_text, parse_mode="HTML")


def register(application: Application):
    application.add_handler(CommandHandler("profile", profile))