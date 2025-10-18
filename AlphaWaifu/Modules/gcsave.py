# AlphaWaifu/Modules/gcsave.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ChatMemberHandler, ContextTypes
from AlphaWaifu.db import save_group

LOG_CHANNEL_ID = -1002623336438  # 👈 apna log channel ID daalna na bhoolna

# ---------------- GC SAVE HANDLER ---------------- #
async def gc_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    member = update.my_chat_member   # ✅ fix

    # ✅ Check if bot added to group
    if member.new_chat_member and member.new_chat_member.user.id == context.bot.id:
        # Save group in DB
        await save_group(chat.id, chat.title)

        # Only "Add Me" button
        buttons = [
            [InlineKeyboardButton("✦ ➕ ΛDD ME ➕ ✦",
                                  url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ]

        caption = (
            "┏━━━━━━━━━━━━━━━━━━⧫\n"
            "✾ ✦ 𝗔𝗟𝗣𝗛𝗔 X 𝗪𝗔𝗜𝗙𝗨 ✦ ʙᴏᴛ\n"
            "┗━━━━━━━━━━━━━━━━━━⧫\n"
            "┣⪼ Hᴇʏ! Tʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ 💫\n"
            "┣⪼ ᴜsᴇ /guess ᴛᴏ sᴛᴀʀᴛ ғᴜɴ 🎴"
        )

        await context.bot.send_message(
            chat_id=chat.id,
            text=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # ✅ Send log message
        adder = member.from_user.mention_html() if member.from_user else "Unknown"
        log_text = (
            "𝐓ᴇʟᴇɢʀᴀᴍ 𝐖ᴀɪғᴜ 𝐁ᴏᴛ 𝐆ʀᴏᴜᴘ 𝐀ᴅᴅ 💌\n\n"
            f"👥 𝐆ʀᴏᴜᴘ - {chat.title} (`{chat.id}`)\n"
            f"➕ 𝐀ᴅᴅᴇᴅ 𝐁ʏ - {adder}\n\n"
            "𝐒ᴜᴘᴘᴏʀᴛ - @NARUTO_X_SUPPORT 💫\n"
            "𝐎ᴡɴᴇʀ - @Uzumaki_X_Naruto_6 ❤️‍🔥"
        )
        await context.bot.send_message(LOG_CHANNEL_ID, log_text, parse_mode="HTML")


# ---------------- REGISTER HANDLER ---------------- #
def register(application: Application):
    application.add_handler(ChatMemberHandler(gc_save, ChatMemberHandler.MY_CHAT_MEMBER))