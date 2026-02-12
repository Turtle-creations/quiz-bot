import json
import os
from telegram import Update
from telegram.ext import ContextTypes

USERS_FILE = "data/users.json"


# ---------- LOAD USERS ----------
def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


# ---------- SAVE USERS ----------
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ---------- SMART BROADCAST ----------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ⚠️ optional — admin check (apna Telegram ID daalo)
    ADMIN_ID = 123456789  
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed.")
        return

    # message check
    if not context.args:
        await update.message.reply_text("Usage:\n/broadcast Hello users")
        return

    text = " ".join(context.args)

    users = load_users()
    success = 0
    failed = []

    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            success += 1
        except:
            failed.append(uid)

    # ❗ failed users remove
    users = [u for u in users if u not in failed]
    save_users(users)

    await update.message.reply_text(
        f"✅ Sent: {success}\n❌ Removed: {len(failed)}"
    )
