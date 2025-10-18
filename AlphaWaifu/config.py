import os

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "7442709602:AAE0Z65zpbiPnyMRAmxZISKS0m_V3soJd7w"
)
MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb+srv://xolig17286:xolig17286@cluster0.5cysryr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# space-separated IDs as default
SUDO_USERS = [
    int(x) for x in os.getenv(
        "SUDO_USERS",
        "7576729648 7692444709 6642049252 6239769036"
    ).split()
]

CHARA_CHANNEL_ID = -1002527530412

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