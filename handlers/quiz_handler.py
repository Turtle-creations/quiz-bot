import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ---- GLOBAL STORAGE ----
order = {}
index = {}
score = {}

from data.questions import QUESTIONS


# ================= QUIZ START =================
async def quiz(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    order[uid] = random.sample(
        range(len(QUESTIONS)),
        min(100, len(QUESTIONS))
    )
    index[uid] = 0
    score[uid] = 0

    await send_question(query, uid)


# ================= SEND QUESTION =================
async def send_question(query, uid):

    i = index[uid]

    if i >= len(order[uid]):
        await query.edit_message_text(
            f"🏁 Quiz Finished!\n\nScore: {score[uid]}/{len(order[uid])}"
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
        f"Choose the correct option below:"
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


# ================= ANSWER =================
async def answer(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    choice = int(query.data.split("_")[1])

    q = QUESTIONS[order[uid][index[uid]]]

    if choice == q["correct"]:
        score[uid] += 1

    index[uid] += 1

    await send_question(query, uid)


# ================= RESTART =================
async def restart(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    order[uid] = random.sample(
        range(len(QUESTIONS)),
        min(100, len(QUESTIONS))
    )
    index[uid] = 0
    score[uid] = 0

    await send_question(query, uid)


# ================= STOP =================
async def stop(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    text = (
        "⛔ Quiz Stopped\n\n"
        f"Your Score: {score.get(uid,0)}/{index.get(uid,0)}\n"
        "You can restart anytime from menu."
    )

    await query.edit_message_text(text)


# ================= QUIZ SIZE =================
async def set_quiz_size(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    size = int(query.data.split("_")[1])

    order[uid] = random.sample(
        range(len(QUESTIONS)),
        min(size, len(QUESTIONS))
    )
    index[uid] = 0
    score[uid] = 0

    await send_question(query, uid)


# ================= LEADERBOARD =================
async def show_leaderboard(update, context):
    if update.message:
        await update.message.reply_text("🏆 Leaderboard coming soon")
    else:
        await update.callback_query.message.reply_text("🏆 Leaderboard coming soon")
