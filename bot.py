from flask import Flask
import threading
import os
import logging
import asyncio

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ---------------- Flask Setup ----------------
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "I am alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    threading.Thread(target=run_flask, daemon=True).start()

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO)

# ---------------- Bot Imports ----------------
TOKEN = os.environ.get("TOKEN")

from database.db import init_db
from handlers.start_handler import (
    start, quiz, answer, stop, restart,
    show_leaderboard, set_quiz_size
)
from handlers.admin_handler import admin_panel
from handlers.admin_actions import handle_admin_buttons, handle_admin_text


# ---------------- MAIN ----------------
async def main():

    print("Starting Flask and Bot...")
    keep_alive()
    init_db()

    bot_app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("leaderboard", show_leaderboard))
    bot_app.add_handler(CommandHandler("admin", admin_panel))

    bot_app.add_handler(CallbackQueryHandler(quiz, pattern="^startquiz$"))
    bot_app.add_handler(CallbackQueryHandler(answer, pattern="^ans_"))
    bot_app.add_handler(CallbackQueryHandler(restart, pattern="^restartquiz$"))
    bot_app.add_handler(CallbackQueryHandler(stop, pattern="^stopquiz$"))
    bot_app.add_handler(CallbackQueryHandler(show_leaderboard, pattern="^showleader$"))
    bot_app.add_handler(CallbackQueryHandler(set_quiz_size, pattern="^set_"))

    bot_app.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_"))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))

    print("BOT IS RUNNING...")

    # 🔥 Correct polling lifecycle
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

    # ✅ KEEP BOT ALIVE (IMPORTANT)
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
