# AlphaWaifu/__init__.py
from telegram.ext import Application
from AlphaWaifu.config import BOT_TOKEN   # apne config se BOT_TOKEN lena

application = Application.builder().token(BOT_TOKEN).build()
