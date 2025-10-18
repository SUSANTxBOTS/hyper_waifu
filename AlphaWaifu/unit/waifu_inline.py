import re
from cachetools import TTLCache
from AlphaWaifu.db import waifu_collection, users_collection

# Caching
all_characters_cache = TTLCache(maxsize=10000, ttl=300)  # 5 min
user_collection_cache = TTLCache(maxsize=10000, ttl=30)  # 30 sec

async def get_user_collection(user_id: int):
    """Get user collection (harem) with caching"""
    user_id = int(user_id)
    if user_id in user_collection_cache:
        return user_collection_cache[user_id]

    user = await users_collection.find_one({"user_id": user_id})
    if user:
        user_collection_cache[user_id] = user
        return user
    return None

async def search_characters(query: str, force_refresh=False):
    """Search characters by name, anime or aliases"""
    cache_key = f"search_{query.lower()}"
    if not force_refresh and cache_key in all_characters_cache:
        return all_characters_cache[cache_key]

    regex = re.compile(query, re.IGNORECASE)
    characters = await waifu_collection.find({
        "$or": [
            {"name": regex},
            {"anime": regex},
            {"aliases": regex}
        ]
    }).to_list(length=None)

    all_characters_cache[cache_key] = characters
    return characters

async def get_all_characters(force_refresh=False):
    """Get all characters"""
    if not force_refresh and "all_characters" in all_characters_cache:
        return all_characters_cache["all_characters"]

    characters = await waifu_collection.find({}).to_list(length=None)
    all_characters_cache["all_characters"] = characters
    return characters

async def refresh_character_caches():
    """Clear all caches"""
    all_characters_cache.clear()
    user_collection_cache.clear()