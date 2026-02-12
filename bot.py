from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import logging

logging.basicConfig(
    level=logging.WARNING
)


from config import TOKEN
from database.db import init_db

from handlers.start_handler import (
    start, quiz, answer, stop, restart,
    show_leaderboard, set_quiz_size
)


from handlers.admin_handler import admin_panel
from handlers.admin_actions import handle_admin_buttons, handle_admin_text
from handlers.start_handler import set_quiz_size

init_db()

app = ApplicationBuilder().token(TOKEN).build()

# COMMANDS
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("leaderboard", show_leaderboard))
app.add_handler(CommandHandler("admin", admin_panel))

# QUIZ
app.add_handler(CallbackQueryHandler(quiz, pattern="^startquiz$"))
app.add_handler(CallbackQueryHandler(answer, pattern="^ans_"))
app.add_handler(CallbackQueryHandler(restart, pattern="^restartquiz$"))
app.add_handler(CallbackQueryHandler(stop, pattern="^stopquiz$"))
app.add_handler(CallbackQueryHandler(show_leaderboard, pattern="^showleader$"))
app.add_handler(CallbackQueryHandler(set_quiz_size, pattern="^set_"))

# ADMIN
app.add_handler(CallbackQueryHandler(handle_admin_buttons, pattern="^admin_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))

app.run_polling(drop_pending_updates=True)
print("BOT RUNNING...")
