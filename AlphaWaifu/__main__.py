import logging
from telegram.ext import Application
from AlphaWaifu.config import BOT_TOKEN
from AlphaWaifu.Modules import start, upload, guess, changetime, autodrop, reset, gacha, check, rarities, profile, harem, inline, leaderboard, aclaim, give, gift, trade, fav, rupload, redeem, credeem, bcast, gcsave, uploader

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register all handlers
    start.register(application)
    upload.register(application)
    guess.register(application)
    changetime.register(application)
    autodrop.register(application)
    reset.register(application)
    gacha.register(application)
    check.register(application)
    rarities.register(application)
    profile.register(application)
    harem.register(application)
    inline.register(application)
    leaderboard.register(application)
    aclaim.register(application)
    give.register(application)
    gift.register(application)
    trade.register(application)
    fav.register(application)
    rupload.register(application)
    redeem.register(application)
    credeem.register(application)
    bcast.register(application)
    uploader.register(application)
    
    print("🚀 AlphaWaifu Bot Started!")
    application.run_polling()

if __name__ == "__main__":
    main()