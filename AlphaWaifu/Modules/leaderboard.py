# AlphaWaifu/Modules/leaderboard.py

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from AlphaWaifu.db import users_collection, groups_collection, guesses_collection


# ------------------ Helper ------------------ #
async def get_user_name(user_id: int) -> str:
    """Get best possible display name for a user."""
    user = await users_collection.find_one({"user_id": user_id})
    if user:
        return user.get("first_name") or user.get("username") or "Unknown"

    guess = await guesses_collection.find_one({"user_id": user_id})
    if guess:
        return guess.get("first_name") or guess.get("username") or "Unknown"

    return "Unknown"


# ------------------ /top ------------------ #
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pipeline = [
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = await guesses_collection.aggregate(pipeline).to_list(length=10)

    if not results:
        return await update.message.reply_text("❌ No guesses found yet!")

    text = "🌐 𝗚𝗟𝗢𝗕𝗔𝗟 𝗧𝗢𝗣 𝗚𝗨𝗘𝗦𝗦𝗘𝗥𝗦:\n"
    text += "┏━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┓\n"

    rank = 1
    for res in results:
        name = await get_user_name(res["_id"])
        text += f"┣ {rank:02d}. {name} ⇒ {res['count']}\n"
        rank += 1

    text += "┗━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┛"
    await update.message.reply_text(text)


# ------------------ /top_gc ------------------ #
async def top_gc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pipeline = [
        {"$group": {"_id": "$chat_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = await guesses_collection.aggregate(pipeline).to_list(length=10)

    if not results:
        return await update.message.reply_text("❌ No group guesses found yet!")

    text = "🌐 𝗚𝗟𝗢𝗕𝗔𝗟 𝗧𝗢𝗣 𝗚𝗥𝗢𝗨𝗣𝗦:\n"
    text += "┏━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┓\n"

    rank = 1
    for res in results:
        group = await groups_collection.find_one({"chat_id": res["_id"]})
        if group:
            title = group.get("title", f"Chat {res['_id']}")
        else:
            guess = await guesses_collection.find_one({"chat_id": res["_id"]})
            title = guess.get("chat_title", f"Chat {res['_id']}") if guess else f"Chat {res['_id']}"

        text += f"┣ {rank:02d}. {title} ⇒ {res['count']}\n"
        rank += 1

    text += "┗━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┛"
    await update.message.reply_text(text)


# ------------------ /coin_top ------------------ #
async def coin_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = users_collection.find().sort("coins", -1).limit(10)
    results = await cursor.to_list(length=10)

    if not results:
        return await update.message.reply_text("❌ No coin data available!")

    text = "💰 𝗧𝗢𝗣 𝗖𝗢𝗜𝗡 𝗖𝗢𝗟𝗟𝗘𝗖𝗧𝗢𝗥𝗦:\n"
    text += "┏━┅┅┄┄⟞⟦💰⟧⟝┄┄┉┉━┓\n"

    rank = 1
    for user in results:
        name = user.get("first_name") or user.get("username") or "Unknown"
        coins = user.get("coins", 0)
        text += f"┣ {rank:02d}. {name} ⇒ {coins} 🪙\n"
        rank += 1

    text += "┗━┅┅┄┄⟞⟦💰⟧⟝┄┄┉┉━┛"
    await update.message.reply_text(text)


# ------------------ REGISTER ------------------ #
def register(application: Application):
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("top_gc", top_gc))
    application.add_handler(CommandHandler("coin_top", coin_top))