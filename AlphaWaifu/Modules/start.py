# AlphaWaifu/Modules/start.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application
from AlphaWaifu.db import save_user, save_group

# ✅ Apna log channel yaha daalo
LOG_CHANNEL_ID = -1002850320991  # 👈 isko apne log channel ID se replace karo


# ---------------- START HANDLER ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # ✅ Save both user & group if applicable
    if user:
        await save_user(user.id, user.username)
    if chat.type in ["group", "supergroup"]:
        await save_group(chat.id, chat.title)

    # ---------------- PRIVATE CHAT ---------------- #
    if chat.type == "private":
        buttons = [
            [InlineKeyboardButton("✦ ➕ ΛDD ME ➕ ✦", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [
                InlineKeyboardButton("⌬ SᑌPPORƬ ⌬", url="https://t.me/+RwXiTpaDdaliN2Jl"),
                InlineKeyboardButton("⌬ ᑌPᗪΛTES ⌬", url="https://t.me/ThronexCodex"),
            ],
            [
                InlineKeyboardButton("☯ HΞLᑭ ☯", callback_data="help_menu"),
                InlineKeyboardButton("♛ ᗪΞᐯΞᒪOᑭΞᖇ ♛", url="https://t.me/xAkairo"),
            ]
        ]

        caption = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
            "✾ Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ  ˹ᴡᴀɢᴜʀɪ ꭙ ɢʀᴀʙʙᴇʀ˼ 🫧 ,\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
            "┣⪼ ✦ I ᴡɪʟʟ ʜᴇʟᴘ ʏᴏᴜ ғɪɴᴅ ʏᴏᴜʀ 𝗪𝗮𝗶ғᴜ ᴏʀ Hᴜsʙᴀɴᴅᴏ\n"
            "┃        ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ.\n"
            "┣⪼ ✦ Yᴏᴜ ᴄᴀɴ sᴇᴀʟ ᴛʜᴇᴍ ʙʏ /guess ᴄᴏᴍᴍᴀɴᴅ\n"
            "┃        ᴀɴᴅ ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ʜᴀʀᴇᴍ.\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
            "✦ Tᴀᴘ ᴏɴ \"HΞLᑭ\" ғᴏʀ ᴍᴏʀᴇ ᴄᴏᴍᴍᴀɴᴅs. ✦"
        )

        await update.message.reply_photo(
            photo="https://files.catbox.moe/fn9yhx.jpg",
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # ✅ Log who started bot
        log_text = (
            "𝐓ᴇʟᴇɢʀᴀᴍ 𝐖ᴀɪғᴜ 𝐁ᴏᴛ 𝐒ᴛᴀʀᴛ 💌\n\n"
            f"👤 𝐔ꜱᴇʀ - {user.mention_html()} (`{user.id}`)\n"
            f"📝 𝐔ꜱᴇʀɴᴀᴍᴇ - @{user.username if user.username else 'Nᴏɴᴇ'}\n"
            f"🌸 𝐍ᴀᴍᴇ - {user.full_name}\n\n"
            "𝐒ᴜᴘᴘᴏʀᴛ - @OrbinexX_Society 💫\n"
            "𝐎ᴡɴᴇʀ - @xPrimehyper❤️‍🔥"
        )
        await context.bot.send_message(LOG_CHANNEL_ID, log_text, parse_mode="HTML")

    # ---------------- GROUP CHAT ---------------- #
    elif chat.type in ["group", "supergroup"]:
        buttons = [
            [InlineKeyboardButton("✦ ➕ ΛDD ME ➕ ✦", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [
                InlineKeyboardButton("☯ HΞLᑭ ☯", callback_data="help_menu"),
                InlineKeyboardButton("⌬ SᑌPPORƬ ⌬", url="https://t.me/+RwXiTpaDdaliN2Jl"),
            ]
        ]

        caption = (
            "┏━━━━━━━━━━━━━━━━━━⧫\n"
            "✾  ˹ᴡᴀɢᴜʀɪ ꭙ ɢʀᴀʙʙᴇʀ˼ 🫧 \n"
            "┗━━━━━━━━━━━━━━━━━━⧫\n"
            "┣⪼ Hᴇʏ! Tʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ 💫\n"
            "┣⪼ ᴜsᴇ /guess ᴛᴏ sᴛᴀʀᴛ ғᴜɴ 🎴"
        )

        await update.message.reply_text(
            text=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        # ✅ Log group add
        adder = user.mention_html() if user else "Unknown"
        log_text = (
            "𝐓ᴇʟᴇɢʀᴀᴍ 𝐖ᴀɪғᴜ 𝐁ᴏᴛ 𝐆ʀᴏᴜᴘ 𝐀ᴅᴅ 💌\n\n"
            f"👥 𝐆ʀᴏᴜᴘ - {chat.title} (`{chat.id}`)\n"
            f"➕ 𝐀ᴅᴅᴇᴅ 𝐁ʏ - {adder}\n\n"
            "𝐒ᴜᴘᴘᴏʀᴛ - @NARUTO_X_SUPPORT 💫\n"
            "𝐎ᴡɴᴇʀ - @Uzumaki_X_Naruto_6 ❤️‍🔥"
        )
        await context.bot.send_message(LOG_CHANNEL_ID, log_text, parse_mode="HTML")


# ---------------- HELP HANDLER ---------------- #
HELP_TEXT = """
┏━━━━━━━━━━━━━ HELP ━━━━━━━━━━━━━⧫

🎴 *Game & Collection*
/guess - Guess a character (group only)
/fav - Set your favorite character
/trade - Trade characters
/gift - Gift a character (group only)
/collection - View your collection
/topgroups - See top guessing groups
/top - See top users
/ctop - Chat top users
/changetime - Change spawn time (group only)

💰 *Rewards & Balance*
/aclaim - Claim your free waifu
/redeem - Redeem a code
/credeem - Redeem coins
/daily - Claim your daily rewards
/weekly - Claim your weekly rewards
/bonus - Claim your bonus
/balance - Check your balance

👥 *Profile & Info*
/check - Check waifu by ID
/profile - See your profile
/harem - See your harem
/rarities - Check rarities

🏆 *Ranks*
/top - See top collectors
/top_gc - See top group chats
/coin_top - See top coins collector

⚙️ *Admin Only*
/bcast - Broadcast a message
/reset - Reset a user’s data
/reset_all - Reset all data

🚀 *General*
/start - ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ

┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
"""

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton("◀️ ᗷΛᑕK", callback_data="back_to_start")]]
    if update.callback_query:
        await update.callback_query.message.edit_text(
            HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            HELP_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown"
        )

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "back_to_start":
        fake_update = Update(update.update_id, message=query.message)
        fake_update.effective_chat = query.message.chat
        fake_update.effective_user = query.from_user
        await start(fake_update, context)


# ---------------- REGISTER HANDLERS ---------------- #
def register(application: Application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CallbackQueryHandler(help_menu, pattern="help_menu"))
    application.add_handler(CallbackQueryHandler(help_callback, pattern="back_to_start"))
