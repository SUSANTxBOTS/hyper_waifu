from collections import defaultdict, Counter
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo
)
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, Application
from AlphaWaifu.db import users_collection, waifu_collection, RARITY_MAP


# ---------- FORMAT HAREM WITH COUNTS ----------
def format_harem(user_first_name: str, harem: list, page: int, per_page: int = 10):
    grouped = defaultdict(list)
    for w in harem:
        # normalize anime name
        anime_name = w["anime"].replace("_", " ").strip()
        grouped[anime_name].append(w)

    # count duplicates inside each anime
    grouped_counts = {}
    for anime, chars in grouped.items():
        counter = Counter([c["waifu_id"] for c in chars])
        merged = []
        for waifu_id, count in counter.items():
            first = next(c for c in chars if c["waifu_id"] == waifu_id)
            merged.append({
                "waifu_id": waifu_id,
                "name": first["name"],
                "rarity": first["rarity"],
                "count": count
            })
        grouped_counts[anime] = merged

    animes = list(grouped_counts.items())
    flat_list = [(anime, w) for anime, chars in animes for w in chars]

    total_pages = (len(flat_list) + per_page - 1) // per_page
    start, end = (page - 1) * per_page, page * per_page
    selected = flat_list[start:end]

    text = f"『{user_first_name}』's Harem - Page {page}/{total_pages}\n\n"

    current_anime = None
    for anime, w in selected:
        if current_anime != anime:
            if current_anime:
                text += "\n"
            text += f"⌬ {anime}\n"
            current_anime = anime
        rarity = RARITY_MAP.get(w['rarity'], "❓")
        text += f"◈ {rarity.split()[0]} {w['waifu_id']} {w['name']} ×{w['count']}\n"

    return text.strip(), total_pages


# ---------- HELPER: Get Display Waifu ----------
async def get_display_waifu(user_id: int, harem: list):
    """Return waifu doc for fav > last guess > fallback first harem"""
    user_doc = await users_collection.find_one({"user_id": user_id})

    waifu_id = None
    if user_doc and user_doc.get("fav_waifu_id"):
        waifu_id = user_doc["fav_waifu_id"]
    elif user_doc and user_doc.get("last_guess_id"):
        waifu_id = user_doc["last_guess_id"]
    elif harem:
        waifu_id = harem[0]["waifu_id"]

    if not waifu_id:
        return None
    return await waifu_collection.find_one({"waifu_id": waifu_id})


# ---------- HAREM COMMAND ----------
async def harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = await users_collection.find_one({"user_id": user.id})

    if not user_data or "harem" not in user_data or not user_data["harem"]:
        return await update.message.reply_text("❌ Your harem is empty.")

    harem = user_data["harem"]
    caption, total_pages = format_harem(user.first_name, harem, page=1)

    # buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "📂 COLLECTION",
                switch_inline_query_current_chat=f"collection.{user.id}"
            ),
            InlineKeyboardButton(
                "🎬 AMV",
                switch_inline_query_current_chat=f"collection.{user.id}.AMV"
            )
        ]
    ]
    if total_pages > 1:
        keyboard.append([InlineKeyboardButton("NEXT ➡", callback_data=f"harem_next_2_{total_pages}")])
    keyboard.append([InlineKeyboardButton("CLOSE", callback_data="harem_close")])

    # show waifu image
    waifu_doc = await get_display_waifu(user.id, harem)
    if waifu_doc and waifu_doc.get("media_type") == "photo":
        await context.bot.send_photo(
            update.effective_chat.id,
            photo=waifu_doc["file_id"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif waifu_doc and waifu_doc.get("media_type") == "video":
        await context.bot.send_video(
            update.effective_chat.id,
            video=waifu_doc["file_id"],
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(keyboard))


# ---------- PAGINATION HANDLER ----------
async def harem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user = query.from_user
    user_data = await users_collection.find_one({"user_id": user.id})
    if not user_data or "harem" not in user_data:
        return await query.edit_message_text("❌ Your harem is empty.")

    harem = user_data["harem"]

    if data.startswith("harem_next_") or data.startswith("harem_prev_"):
        _, action, page, total_pages = data.split("_")
        page, total_pages = int(page), int(total_pages)
        caption, _ = format_harem(user.first_name, harem, page)

        keyboard = [
            [
                InlineKeyboardButton(
                    "📂 COLLECTION",
                    switch_inline_query_current_chat=f"collection.{user.id}"
                ),
                InlineKeyboardButton(
                    "🎬 AMV",
                    switch_inline_query_current_chat=f"collection.{user.id}.AMV"
                )
            ]
        ]
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅ PREV", callback_data=f"harem_prev_{page-1}_{total_pages}"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("NEXT ➡", callback_data=f"harem_next_{page+1}_{total_pages}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("CLOSE", callback_data="harem_close")])

        waifu_doc = await get_display_waifu(user.id, harem)
        if waifu_doc and waifu_doc.get("media_type") == "photo":
            await query.edit_message_media(
                media=InputMediaPhoto(waifu_doc["file_id"], caption=caption),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        elif waifu_doc and waifu_doc.get("media_type") == "video":
            await query.edit_message_media(
                media=InputMediaVideo(waifu_doc["file_id"], caption=caption),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await query.edit_message_text(caption, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "harem_close":
        await query.delete_message()


# ---------- REGISTER ----------
def register(application: Application):
    application.add_handler(CommandHandler("harem", harem))
    application.add_handler(CallbackQueryHandler(harem_callback, pattern="^harem_"))