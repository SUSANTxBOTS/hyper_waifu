# AlphaWaifu/Modules/rarities.py

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import waifu_collection, RARITY_MAP


# ----------------- /rarities ----------------- #
async def rarities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # aggregate rarity counts
    pipeline = [
        {"$group": {"_id": "$rarity", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = await waifu_collection.aggregate(pipeline).to_list(length=None)

    # convert to dict {rarity_code: count}
    rarity_counts = {r["_id"]: r["count"] for r in results}
    total = sum(rarity_counts.values())

    # build text
    text = "✨ Character Count by Rarity ✨\n\n"
    for rarity_code, rarity_name in RARITY_MAP.items():
        count = rarity_counts.get(rarity_code, 0)
        text += f"◈ {rarity_name} {count} character(s)\n"

    text += f"\n🌟 Total Characters: {total}\n"

    await update.message.reply_text(text)


# ----------------- Register ----------------- #
def register(application: Application):
    application.add_handler(CommandHandler("rarities", rarities))