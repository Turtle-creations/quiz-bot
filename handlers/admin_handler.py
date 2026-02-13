from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMIN_IDS

# -------- ADMIN PANEL --------
async def admin_panel(update, context):
    # user id safely lo (message ya callback dono me chale)
    user = update.effective_user
    uid = user.id if user else None

    # -------- CHECK ADMIN --------
    if uid not in ADMIN_IDS:
        if update.message:
            await update.message.reply_text("❌ You are not admin")
        elif update.callback_query:
            await update.callback_query.answer("❌ You are not admin", show_alert=True)
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

    text = "⚙️ Admin Panel"

    # -------- SEND PANEL (safe) --------
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text, reply_markup=reply_markup)
