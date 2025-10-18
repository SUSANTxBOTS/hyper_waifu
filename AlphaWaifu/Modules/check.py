# AlphaWaifu/Modules/check.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application
from AlphaWaifu.db import waifu_collection, users_collection, guesses_collection, RARITY_MAP


# ----------------- /check ----------------- #
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        return await update.message.reply_text("❌ Usage: `/check <waifu_id>`", parse_mode="Markdown")

    waifu_id = context.args[0].zfill(2)   # ensure "01", "02" format
    waifu = await waifu_collection.find_one({"waifu_id": waifu_id})

    if not waifu:
        return await update.message.reply_text("❌ Waifu not found in database!")

    rarity = RARITY_MAP.get(waifu["rarity"], "❓ Unknown")

    text = f"""
╔═══════◇◆◇═══════╗
      💫 C H A R A C T E R   I N F O
╚═══════◇◆◇═══════╝

┏━━━━━━━━━━━━━━━━━━━━━┓
┃ 🆔  Iᴅ       :  {waifu['waifu_id']}
┃ 🧿  Nᴀᴍᴇ    :  {waifu['name']}
┃ 📺  Aɴɪᴍᴇ   :  {waifu['anime']}
┃ 💎  Rᴀʀɪᴛʏ  :  {rarity}
┗━━━━━━━━━━━━━━━━━━━━━┛
"""

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🌍 WHO HAVE IT", callback_data=f"whohave_{waifu_id}")]]
    )

    if waifu.get("media_type") == "photo":
        await update.message.reply_photo(photo=waifu["file_id"], caption=text, reply_markup=button)
    elif waifu.get("media_type") == "video":
        await update.message.reply_video(video=waifu["file_id"], caption=text, reply_markup=button)
    else:
        await update.message.reply_text(text, reply_markup=button)


# ----------------- Callback: WHO HAVE IT ----------------- #
async def who_have_it(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    waifu_id = query.data.split("_")[1]

    # find all users who own this waifu
    users = await users_collection.find({"harem.waifu_id": waifu_id}).to_list(length=None)

    owners = []
    for user in users:
        count = sum(1 for h in user.get("harem", []) if h["waifu_id"] == waifu_id)
        if count > 0:
            name = (
                f"@{user['username']}"
                if user.get("username")
                else f"{user.get('first_name', 'User')} ({user['user_id']})"
            )
            owners.append((name, count))

    total_count = sum(c for _, c in owners)

    # sort by highest count, take only top 10
    owners_sorted = sorted(owners, key=lambda x: x[1], reverse=True)[:10]

    text = f"""
🌍 Global Count: {total_count} users own this character.

🏆 Top 10 Collectors:
"""
    if not owners_sorted:
        text += "\n❌ Nobody owns this waifu yet!"
    else:
        for i, (name, count) in enumerate(owners_sorted, start=1):
            text += f"{i}. {name} ×{count}\n"

    # ✅ handle caption/text update
    if query.message.photo or query.message.video:
        await query.edit_message_caption(caption=text)
    else:
        await query.edit_message_text(text)


# ----------------- Register ----------------- #
def register(application: Application):
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CallbackQueryHandler(who_have_it, pattern=r"whohave_\d+"))