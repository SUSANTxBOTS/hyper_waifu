import time
from html import escape
from telegram import InlineQueryResultPhoto, InlineQueryResultVideo, Update
from telegram.ext import InlineQueryHandler, ContextTypes, Application
from AlphaWaifu.db import RARITY_MAP
from AlphaWaifu.unit.waifu_inline import (
    get_user_collection,
    search_characters,
    get_all_characters,
    refresh_character_caches,
)

# ---------- INLINE QUERY HANDLER ---------- #
async def inlinequery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.inline_query
        text = query.query.strip()
        offset = int(query.offset) if query.offset else 0

        force_refresh = "!refresh" in text
        if force_refresh:
            text = text.replace("!refresh", "").strip()
            await refresh_character_caches()

        # ---------- USER COLLECTION QUERY ---------- #
        user = None
        if text.startswith("collection."):
            parts = text.split(" ")
            user_id = parts[0].split(".")[1]
            search_terms = " ".join(parts[1:]) if len(parts) > 1 else ""

            if user_id.isdigit():
                user = await get_user_collection(user_id)
                if user:
                    all_characters = list({w["waifu_id"]: w for w in user.get("harem", [])}.values())
                    if search_terms:
                        import re
                        regex = re.compile(search_terms, re.IGNORECASE)
                        all_characters = [
                            w for w in all_characters
                            if regex.search(w.get("name", "")) or regex.search(w.get("anime", ""))
                        ]
                else:
                    all_characters = []
            else:
                all_characters = []
        else:
            if text:
                all_characters = await search_characters(text, force_refresh)
            else:
                all_characters = await get_all_characters(force_refresh)

        # ---------- FILTER MEDIA TYPE ---------- #
        if ".AMV" in text:
            all_characters = [c for c in all_characters if c.get("media_type") == "video"]
        else:
            all_characters = [c for c in all_characters if c.get("media_type") == "photo"]

        # ---------- PAGINATION ---------- #
        characters = all_characters[offset:offset + 50]
        next_offset = str(offset + len(characters)) if len(characters) == 50 else None

        results = []
        for char in characters:
            if not all(k in char for k in ["waifu_id", "name", "anime", "rarity"]):
                continue

            rarity_text = RARITY_MAP.get(char["rarity"], "❓ Unknown")

            if user:
                count = sum(1 for c in user.get("harem", []) if c.get("waifu_id") == char["waifu_id"])
                caption = (
                    f"<b>{escape(user.get('first_name', 'User'))}'s Collection:</b>\n"
                    f"🌸 <b>{escape(char['name'])} (x{count})</b>\n"
                    f"📺 From: {escape(char['anime'])}\n"
                    f"🌟 Rarity: {escape(rarity_text)}\n"
                    f"🆔 <code>{escape(str(char['waifu_id']))}</code>"
                )
            else:
                caption = (
                    f"<b>Character Details:</b>\n\n"
                    f"🌸 {escape(char['name'])}\n"
                    f"📺 From: {escape(char['anime'])}\n"
                    f"🌟 Rarity: {escape(rarity_text)}\n"
                    f"🆔 <code>{escape(str(char['waifu_id']))}</code>"
                )

            if char.get("media_type") == "video":
                results.append(InlineQueryResultVideo(
                    id=f"{char['waifu_id']}_{time.time()}",
                    video_url=char["file_id"],
                    mime_type="video/mp4",
                    thumbnail_url="https://telegra.ph/file/f2d48f9b9dbe52.jpg",
                    title=char["name"],
                    description=f"{char['anime']} | {rarity_text}",
                    caption=caption,
                    parse_mode="HTML"
                ))
            elif char.get("media_type") == "photo":
                results.append(InlineQueryResultPhoto(
                    id=f"{char['waifu_id']}_{time.time()}",
                    photo_url=char["file_id"],
                    thumbnail_url=char["file_id"],
                    caption=caption,
                    parse_mode="HTML"
                ))

        await query.answer(results, cache_time=1, next_offset=next_offset)

    except Exception as e:
        print(f"Inline query error: {e}")
        await update.inline_query.answer([], cache_time=1)


# ---------- REGISTER ---------- #
def register(application: Application):
    application.add_handler(InlineQueryHandler(inlinequery_handler))