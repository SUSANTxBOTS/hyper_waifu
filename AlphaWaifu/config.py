import os

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "7990481567:AAHiI1CQZDuVC0E0OkZIx9a6oP63X7uqLhI"
)
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://Waifu_db_user:3r87a7Wd8mYDcUsy@cluster0.eogfqdu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# space-separated IDs as default
SUDO_USERS = [
    int(x) for x in os.getenv(
        "SUDO_USERS",
        "7125448912"
    ).split()
]

CHARA_CHANNEL_ID = -1002531246021

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
