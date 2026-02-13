from flask import Flask
import threading
import os
import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Flask Setup (Render ko khush rakhne ke liye)
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "I am alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True # Taaki main program band ho toh ye bhi band ho jaye
    t.start()

# Logging setup
logging.basicConfig(level=logging.WARNING)

# Bot logic imports
import os
TOKEN = os.environ.get("TOKEN")
from database.db import init_db
from handlers.start_handler import (
    start, quiz, answer, stop, restart,
    show_leaderboard, set_quiz_size
)
from handlers.admin_handler import admin_panel
from handlers.admin_actions import handle_admin_buttons, handle_admin_text

if __name__ == "__main__":
    print("Starting Flask and Bot...")
    keep_alive() # Flask start hoga
    
    init_db()
    
    # Bot Application setup
    bot_app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("leaderboard", show_leaderboard))
    bot_app.add_handler(CommandHandler("admin", admin_panel))

    # Quiz handlers
    bot_app.add_handler(CallbackQueryHandler(quiz, pattern="^startquiz$"))
    bot_app.add_handler(CallbackQueryHandler(answer, pattern="^ans_"))
    bot_app.add_handler(CallbackQueryHandler(restart, pattern="^restartquiz$"))
    bot_app.add_handler(CallbackQueryHandler(stop, pattern="^stopquiz$"))
    bot_app.add_handler(CallbackQueryHandler(show_leaderboard, pattern="^showleader$"))
    bot_app.add_handler(CallbackQueryHandler(set_quiz_size, pattern="^set_"))

    # Admin handlers
    bot_app.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_"))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))

    print("BOT IS RUNNING...")
    bot_app.run_polling(drop_pending_updates=True)