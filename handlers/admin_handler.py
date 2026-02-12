from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_IDS


async def admin_panel(update, context):

    uid = update.effective_user.id

    # -------- CHECK ADMIN --------
    if uid not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not admin")
        return

    # -------- KEYBOARD --------
    keyboard = [
        [InlineKeyboardButton("➕ Add Question", callback_data="admin_add")],
        [InlineKeyboardButton("📋 View Questions", callback_data="admin_viewq")],
        [InlineKeyboardButton("🗑 Delete Question", callback_data="admin_del")],
        [InlineKeyboardButton("📊 Count Questions", callback_data="admin_count")],
        [InlineKeyboardButton("🏆 Reset Leaderboard", callback_data="admin_reset_lb")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_bc")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # -------- SEND PANEL --------
    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=reply_markup
    )
