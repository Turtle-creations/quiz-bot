import json
import os
from telegram import Update
from telegram.ext import ContextTypes

# ✅ correct place to import
from utils.question_loader import force_reload

QUESTIONS_FILE = "data/questions.json"
USERS_FILE = "data/users.json"


# ---------- HELPERS ----------

def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        return []

    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for q in data:
                q["id"] = int(q["id"])
            return data
    except Exception:
        return []


def save_questions(data):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


# ---------- BUTTON HANDLER ----------

async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # VIEW QUESTIONS
    if data == "admin_viewq":
        questions = load_questions()

        if not questions:
            await query.message.reply_text("No questions found.")
            return

        msg = ""
        for q in questions:
            msg += f"\nID {q['id']}\n{q['question']}\n"
            for opt in q["options"]:
                msg += f"{opt}\n"
            msg += f"✅ Ans: {q['answer']+1}\n"

        await query.message.reply_text(msg)

    # DELETE MODE
    elif data == "admin_del":
        context.user_data["await_delete_id"] = True
        await query.message.reply_text("🗑 Send Question ID to delete")

    # COUNT
    elif data == "admin_count":
        q = load_questions()
        await query.message.reply_text(f"📊 Total Questions: {len(q)}")

    # RESET LEADERBOARD
    elif data == "admin_reset_lb":
        from services.quiz_service import leaderboard
        leaderboard.clear()
        await query.message.reply_text("🏆 Leaderboard Reset")

    # ADD MODE
    elif data == "admin_add":
        context.user_data["admin_mode"] = "add_question"
        await query.message.reply_text(
            "Send question:\n\n"
            "Question\n"
            "Opt1\nOpt2\nOpt3\nOpt4\n"
            "Correct(1-4)"
        )

    # BROADCAST MODE
    elif data == "admin_bc":
        context.user_data["await_broadcast"] = True
        await query.message.reply_text("📢 Send message to broadcast")


# ---------- TEXT HANDLER ----------

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # ---------- ADD QUESTION ----------
    if context.user_data.get("admin_mode") == "add_question":

        lines = text.split("\n")

        if len(lines) < 6:
            await update.message.reply_text("❌ Format wrong")
            return

        question = lines[0]
        options = lines[1:5]

        try:
            answer = int(lines[5]) - 1
            if answer not in range(4):
                raise ValueError
        except:
            await update.message.reply_text("❌ Answer must be 1-4")
            return

        data = load_questions()

        ids = [int(q["id"]) for q in data] if data else []
        new_id = (max(ids) if ids else 0) + 1

        data.append({
            "id": new_id,
            "question": question,
            "options": options,
            "answer": answer
        })

        save_questions(data)

        # ✅ AUTO RELOAD QUESTIONS
        force_reload()

        context.user_data["admin_mode"] = None
        await update.message.reply_text(f"✅ Added with ID {new_id}")
        return


    # ---------- DELETE ----------
    if context.user_data.get("await_delete_id"):

        data = load_questions()
        new_data = [q for q in data if str(q["id"]) != text]

        if len(new_data) == len(data):
            await update.message.reply_text("❌ ID not found")
        else:
            save_questions(new_data)

            # ✅ AUTO RELOAD
            force_reload()

            await update.message.reply_text("✅ Deleted")

        context.user_data["await_delete_id"] = False
        return


    # ---------- BROADCAST ----------
    if context.user_data.get("await_broadcast"):

        users = load_users()

        sent = 0
        for uid in users:
            try:
                await context.bot.send_message(int(uid), text)
                sent += 1
            except:
                pass

        context.user_data["await_broadcast"] = False
        await update.message.reply_text(f"✅ Sent to {sent}")
