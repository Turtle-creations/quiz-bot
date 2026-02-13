import random
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

# ---- GLOBAL STORAGE ----
order = {}
index = {}
score = {}
quiz_size = {}

from utils.question_loader import load_questions


# ================= QUIZ START =================
async def quiz(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    QUESTIONS = load_questions()

    size = quiz_size.get(uid, 10)

    order[uid] = random.sample(
        range(len(QUESTIONS)),
        min(size, len(QUESTIONS))
    )
    index[uid] = 0
    score[uid] = 0

    await send_question(query, uid)


# ================= SEND QUESTION =================
async def send_question(query, uid):
    QUESTIONS = load_questions()

    try:
        if uid not in order:
            return

        i = index.get(uid, 0)

        if i >= len(order[uid]):
            await query.edit_message_text(
                f"🏁 Quiz Finished!\n\nScore: {score.get(uid,0)}/{len(order[uid])}"
            )
            return

        q = QUESTIONS[order[uid][i]]

        buttons = [
            [InlineKeyboardButton(opt, callback_data=f"ans_{n}")]
            for n, opt in enumerate(q["options"])
        ]

        buttons.append([
            InlineKeyboardButton("🔄 Restart", callback_data="restartquiz"),
            InlineKeyboardButton("⛔ Stop", callback_data="stopquiz"),
        ])

        text = (
            f"❓ Question {i+1}/{len(order[uid])}\n\n"
            f"{q['question']}\n\n"
            f"Choose option:"
        )

        try:
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except:
            await query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except Exception:
        logger.exception("Send question crash")


# ================= ANSWER =================
async def answer(update, context):
    QUESTIONS = load_questions()
    try:
        query = update.callback_query
        await query.answer()

        uid = query.from_user.id

        if uid not in order:
            return

        choice = int(query.data.split("_")[1])
        q = QUESTIONS[order[uid][index[uid]]]

        # ✅ JSON me key "answer" hai
        if choice == q["answer"]:
            score[uid] += 1

        index[uid] += 1

        await send_question(query, uid)

    except Exception:
        logger.exception("Answer crash")


# ================= RESTART =================

async def restart(update, context):
    try:
        query = update.callback_query
        await query.answer()

        uid = query.from_user.id

        QUESTIONS = load_questions()

        if not QUESTIONS:
            await query.edit_message_text("❌ No questions available")
            return

        size = quiz_size.get(uid, 10)

        order[uid] = random.sample(
            range(len(QUESTIONS)),
            min(size, len(QUESTIONS))
        )

        index[uid] = 0
        score[uid] = 0

        await send_question(query, uid)

    except Exception:
        logger.exception("Restart crash")

    


# ================= STOP =================
async def stop(update, context):
    try:
        query = update.callback_query
        await query.answer()

        uid = query.from_user.id

        text = (
            "⛔ Quiz Stopped\n\n"
            f"Score: {score.get(uid,0)}/{index.get(uid,0)}"
        )

        await query.edit_message_text(text)

        # cleanup memory
        order.pop(uid, None)
        index.pop(uid, None)
        score.pop(uid, None)

    except Exception:
        logger.exception("Stop crash")


# ================= SET QUIZ SIZE =================
async def set_quiz_size(update, context):
    try:
        query = update.callback_query
        await query.answer()

        uid = query.from_user.id
        size = int(query.data.split("_")[1])

        quiz_size[uid] = size

        await query.edit_message_text(
            f"✅ Quiz size set to {size}\nPress Start Quiz"
        )

    except Exception:
        logger.exception("Set size crash")


# ================= LEADERBOARD =================
async def show_leaderboard(update, context):
    try:
        if update.message:
            await update.message.reply_text("🏆 Leaderboard soon")
        else:
            await update.callback_query.answer("Coming soon")

    except Exception:
        logger.exception("Leaderboard crash")
