# AlphaWaifu/Modules/gift.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application
from AlphaWaifu.db import users_collection, guesses_collection, add_to_harem


# -------------------- GIFT -------------------- #
async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user

    # ✅ Target user (reply or username/userid)
    target = None
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
    elif context.args:
        user_arg = context.args[0]
        if user_arg.startswith("@"):
            db_user = await users_collection.find_one({"username": user_arg[1:]})
            if db_user:
                target = type("Target", (), {
                    "id": db_user["user_id"],
                    "first_name": db_user.get("first_name", user_arg)
                })()
        elif user_arg.isdigit():
            db_user = await users_collection.find_one({"user_id": int(user_arg)})
            if db_user:
                target = type("Target", (), {
                    "id": db_user["user_id"],
                    "first_name": db_user.get("first_name", f"User{user_arg}")
                })()
        else:
            return await update.message.reply_text("❌ Invalid user format!")
    else:
        return await update.message.reply_text("⚠️ Usage: Reply `/gift` or `/gift @username`")

    if not target:
        return await update.message.reply_text("❌ Target user not found!")

    # 🔍 Check sender ke harem me waifu hai?
    user_data = await users_collection.find_one({"user_id": sender.id})
    if not user_data or "harem" not in user_data or not user_data["harem"]:
        return await update.message.reply_text("😔 You don’t have any waifus to gift!")

    waifu = user_data["harem"][-1]  # 🌀 Latest waifu ko gift karenge

    # 🔍 Check guesses_collection
    guessed = await guesses_collection.find_one({"user_id": sender.id, "waifu_id": waifu["waifu_id"]})
    if not guessed:
        return await update.message.reply_text("⚠️ You can only gift waifus that you have guessed!")

    # 🎁 Confirmation Message
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Gift", callback_data=f"confirm_gift:{sender.id}:{target.id}:{waifu['waifu_id']}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_gift:{sender.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎁 『{sender.first_name}』, do you confirm gifting **{waifu['name']}** "
        f"to 『{target.first_name}』?",
        reply_markup=reply_markup
    )


# -------------------- CALLBACK -------------------- #
async def gift_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split(":")

    if data[0] == "confirm_gift":
        sender_id = int(data[1])
        target_id = int(data[2])
        waifu_id = data[3]

        # 🔍 Waifu fetch BEFORE removing
        waifu_doc = await users_collection.find_one(
            {"user_id": sender_id, "harem.waifu_id": waifu_id},
            {"harem.$": 1}
        )

        if not waifu_doc or "harem" not in waifu_doc:
            return await query.edit_message_text("❌ Waifu not found in sender harem!")

        gifted_waifu = waifu_doc["harem"][0]

        # 🔍 Remove from sender
        await users_collection.update_one(
            {"user_id": sender_id},
            {"$pull": {"harem": {"waifu_id": waifu_id}}}
        )

        # 🎀 Add to target harem
        await add_to_harem(
            user_id=target_id,
            waifu=gifted_waifu,
            chat_id=query.message.chat.id
        )

        # 🎉 Success msg
        await query.edit_message_text(
            f"🎉 You have successfully gifted **{gifted_waifu['name']}** "
            f"to [User](tg://user?id={target_id})! 🥳",
            parse_mode="Markdown"
        )

    elif data[0] == "cancel_gift":
        await query.edit_message_text("❌ Gift cancelled!")


# -------------------- REGISTER -------------------- #
def register(application: Application):
    application.add_handler(CommandHandler("gift", gift))
    application.add_handler(CallbackQueryHandler(gift_callback, pattern="^(confirm_gift|cancel_gift):"))