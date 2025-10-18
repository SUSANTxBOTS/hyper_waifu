import re
import random
from datetime import datetime
import motor.motor_asyncio
from cachetools import TTLCache

# ---------- DATABASE SETUP ---------- #
MONGO_URI = "mongodb+srv://xolig17286:xolig17286@cluster0.5cysryr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client["AlphaWaifu"]

# ---------- COLLECTIONS ---------- #
users_collection = db["users"]
groups_collection = db["groups"]
waifu_collection = db["waifus"]
guesses_collection = db["guesses"]
settings_collection = db["settings"]
redeem_codes_collection = db["redeem_collection"]
uploaders_collection = db["uploader_collection"]

# ---------- CACHE SETUP ---------- #
all_characters_cache = TTLCache(maxsize=10000, ttl=300)   # 5 min
user_collection_cache = TTLCache(maxsize=10000, ttl=30)   # 30 sec

# ---------- ACTIVE DROPS ---------- #
CURRENT_DROPS = {}

# ---------- RARITY MAP ---------- #
RARITY_MAP = {
    1: "⚪️ Common",
    2: "🟣 Rare",
    3: "🟡 Legendary",
    4: "🟢 Medium",
    5: "💮 Special Edition",
    6: "🔮 Limited Edition",
    7: "💸 Premium Edition",
    8: "🌤 Summer",
    9: "🎐 Celestial",
    10: "❄️ Winter",
    11: "💝 Valentine",
    12: "🎃 Halloween",
    13: "🎄 Christmas Special",
    14: "🪐 Omniversal 🪐",
    15: "🎭 Cosplay Master 🎭",
    16: "🎗️ AMV Edition",
    17: "🧧 Events",
    18: "🍑 Ecchi",
}

# ---------- FUNCTIONS ---------- #

# Get user collection (harem)
async def get_user_collection(user_id):
    """Get user collection from AlphaBot DB with caching"""
    user_id = int(user_id)
    if user_id in user_collection_cache:
        return user_collection_cache[user_id]

    user = await users_collection.find_one({"user_id": user_id})
    if user:
        harem = user.get("harem", [])
        user_collection_cache[user_id] = harem
        return harem
    return []

# Search characters
async def search_characters(query, force_refresh=False):
    """Search characters from waifu_collection"""
    cache_key = f"search_{query.lower()}"
    if not force_refresh and cache_key in all_characters_cache:
        return all_characters_cache[cache_key]

    regex = re.compile(query, re.IGNORECASE)
    characters = await waifu_collection.find({
        "$or": [
            {"name": regex},
            {"anime": regex},
            {"aliases": regex}  # Support for aliases
        ]
    }).to_list(length=None)

    all_characters_cache[cache_key] = characters
    return characters

# Get all characters
async def get_all_characters(force_refresh=False):
    """Get all characters from waifu_collection"""
    if not force_refresh and "all_characters" in all_characters_cache:
        return all_characters_cache["all_characters"]

    characters = await waifu_collection.find({}).to_list(length=None)
    all_characters_cache["all_characters"] = characters
    return characters

# Force refresh caches
async def refresh_character_caches():
    all_characters_cache.clear()
    user_collection_cache.clear()

# Get next waifu_id (check waifu_collection + redeem_codes_collection)
async def get_next_global_waifu_id() -> str:
    last1 = await waifu_collection.find().sort("waifu_id", -1).to_list(1)
    id1 = int(last1[0]["waifu_id"]) if last1 else 0

    last2 = await redeem_codes_collection.find().sort("waifu_id", -1).to_list(1)
    id2 = int(last2[0]["waifu_id"]) if last2 else 0

    return str(max(id1, id2) + 1).zfill(2)

# Save user
async def save_user(user_id: int, username: str = None, first_name: str = None):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "username": username,
            "first_name": first_name,
            "joined_at": datetime.utcnow()
        }},
        upsert=True,
    )

# Update coins
async def update_coins(user_id: int, amount: int):
    await users_collection.update_one(
        {"user_id": user_id}, {"$inc": {"coins": amount}}, upsert=True
    )

async def get_coins(user_id: int) -> int:
    user = await users_collection.find_one({"user_id": user_id})
    return user.get("coins", 0) if user else 0

# Update tokens
async def update_tokens(user_id: int, amount: int):
    await users_collection.update_one(
        {"user_id": user_id}, {"$inc": {"tokens": amount}}, upsert=True
    )

async def get_tokens(user_id: int) -> int:
    user = await users_collection.find_one({"user_id": user_id})
    return user.get("tokens", 0) if user else 0

# Add to harem
async def add_to_harem(user_id: int, waifu: dict, chat_id: int, first_name: str = None, username: str = None):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$push": {"harem": {
            "waifu_id": waifu["waifu_id"],
            "name": waifu["name"],
            "anime": waifu["anime"],
            "rarity": waifu["rarity"],
            "chat_id": chat_id,
            "captured_at": datetime.utcnow(),
            "user_first_name": first_name,
            "user_username": username
        }}},
        upsert=True
    )

# Save group
async def save_group(chat_id: int, title: str = None):
    await groups_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"title": title, "added_at": datetime.utcnow()}},
        upsert=True,
    )

# Get random waifu
async def get_random_waifu() -> dict:
    count = await waifu_collection.count_documents({})
    if count == 0:
        return None
    index = random.randint(0, count - 1)
    waifu = await waifu_collection.find().skip(index).to_list(1)
    return waifu[0] if waifu else None

# Add guess
async def add_guess(user_id: int, chat_id: int, waifu_id: str, first_name: str = None, username: str = None):
    await guesses_collection.insert_one({
        "user_id": user_id,
        "chat_id": chat_id,
        "waifu_id": waifu_id,
        "first_name": first_name,
        "username": username,
        "guessed_at": datetime.utcnow()
    })