from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from AlphaWaifu.db import users_collection, update_coins, update_tokens, get_coins, get_tokens


# ----------------- Helper ----------------- #
async def can_claim(user_id: int, claim_type: str, cooldown: int) -> bool:
    """Check if user can claim reward"""
    user = await users_collection.find_one({"user_id": user_id})
    now = datetime.utcnow()

    if not user or claim_type not in user:
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {claim_type: now}},
            upsert=True,
        )
        return True

    last_claim = user[claim_type]
    if now - last_claim >= timedelta(seconds=cooldown):
        await users_collection.update_one(
            {"user_id": user_id},
            {"$set": {claim_type: now}},
            upsert=True,
        )
        return True
    return False


# ----------------- Mention Helper ----------------- #
def get_mention(user):
    if user.username:
        return f"@{user.username}"
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"


# ----------------- /daily ----------------- #
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not await can_claim(user_id, "last_daily", 24 * 3600):
        return await update.message.reply_text("❌ You already claimed your <b>Daily Reward</b>. Come back tomorrow!", parse_mode="HTML")

    coins, tokens = 500, 2
    await update_coins(user_id, coins)
    await update_tokens(user_id, tokens)

    mention = get_mention(user)

    text = f"""
╔══════════════╗
   🎁 <b>𝗗𝗔𝗜𝗟𝗬 𝗥𝗘𝗪𝗔𝗥𝗗</b> 🎁
╚══════════════╝

💰 Coins: <b>+{coins}</b>
🪙 Tokens: <b>+{tokens}</b>

✨ Keep grinding, {mention}!
"""
    await update.message.reply_text(text, parse_mode="HTML")


# ----------------- /weekly ----------------- #
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not await can_claim(user_id, "last_weekly", 7 * 24 * 3600):
        return await update.message.reply_text("❌ You already claimed your <b>Weekly Reward</b>. Try next week!", parse_mode="HTML")

    coins, tokens = 4000, 10
    await update_coins(user_id, coins)
    await update_tokens(user_id, tokens)

    mention = get_mention(user)

    text = f"""
╔════════════════╗
   🎉 <b>𝗪𝗘𝗘𝗞𝗟𝗬 𝗥𝗘𝗪𝗔𝗥𝗗</b> 🎉
╚════════════════╝

💰 Coins: <b>+{coins}</b>
🪙 Tokens: <b>+{tokens}</b>

🔥 You're unstoppable, {mention}!
"""
    await update.message.reply_text(text, parse_mode="HTML")


# ----------------- /bonus ----------------- #
async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not await can_claim(user_id, "last_bonus", 12 * 3600):
        return await update.message.reply_text("❌ You already claimed your <b>Bonus Reward</b>. Wait few hours!", parse_mode="HTML")

    coins, tokens = 400, 2
    await update_coins(user_id, coins)
    await update_tokens(user_id, tokens)

    mention = get_mention(user)

    text = f"""
╔══════════════╗
   🎲 <b>𝗕𝗢𝗡𝗨𝗦 𝗥𝗘𝗪𝗔𝗥𝗗</b> 🎲
╚══════════════╝

💰 Coins: <b>+{coins}</b>
🪙 Tokens: <b>+{tokens}</b>

🌌 Luck is on your side, {mention}!
"""
    await update.message.reply_text(text, parse_mode="HTML")


# ----------------- /balance ----------------- #
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    coins = await get_coins(user_id)
    tokens = await get_tokens(user_id)

    text = f"""
╔═══════════════╗
   💼 <b>𝗬𝗢𝗨𝗥 𝗪𝗔𝗟𝗟𝗘𝗧</b> 💼
╚═══════════════╝

💰 Coins: <b>{coins}</b>
🪙 Tokens: <b>{tokens}</b>

⚡ Keep playing to grow your balance!
"""
    await update.message.reply_text(text, parse_mode="HTML")


# ----------------- Register ----------------- #
def register(application: Application):
    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("weekly", weekly))
    application.add_handler(CommandHandler("bonus", bonus))
    application.add_handler(CommandHandler("balance", balance))