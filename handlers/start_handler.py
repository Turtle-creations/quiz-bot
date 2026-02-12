from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.quiz_service import (
    start_user, get_question, answer_question,
    get_score, reset_user, update_leaderboard,
    get_leaderboard, skip_question
)

active_msg = {}
quiz_active = {}
quiz_size_store = {}   # ⭐ store selected size


# ---------- KEYBOARD ----------
def build_keyboard(options):
    kb = [[InlineKeyboardButton(opt, callback_data=f"ans_{i}")]
          for i, opt in enumerate(options)]

    kb.append([
        InlineKeyboardButton("🔄 Restart", callback_data="restartquiz"),
        InlineKeyboardButton("⛔ Stop Quiz", callback_data="stopquiz")
    ])

    return InlineKeyboardMarkup(kb)


# ---------- SEND QUESTION ----------
async def send_question(chat_id, context, uid):

    if not quiz_active.get(uid, False):
        return

    # remove old timer
    for job in context.job_queue.get_jobs_by_name(str(uid)):
        job.schedule_removal()

    qdata = get_question(uid)

    # QUIZ FINISHED
    if not qdata:
        s, total = get_score(uid)
        update_leaderboard(uid)

        await context.bot.send_message(chat_id, f"🏁 Finished!\nScore: {s}/{total}")
        await context.bot.send_message(chat_id, get_leaderboard())

        quiz_active[uid] = False
        return

    text = (
        f"{qdata['question']}\n"
        f"──────────────\n"
        f"⏱ Answer within 15 sec"
    )

    msg = await context.bot.send_message(
        chat_id,
        text,
        reply_markup=build_keyboard(qdata["options"])
    )

    active_msg[uid] = (msg.chat_id, msg.message_id)

    context.job_queue.run_once(
        time_up,
        15,
        data={"uid": uid, "chat": chat_id},
        name=str(uid)
    )


# ---------- TIMEOUT ----------
async def time_up(context):
    uid = context.job.data["uid"]
    chat_id = context.job.data["chat"]

    if not quiz_active.get(uid, False):
        return

    skip_question(uid)
    await context.bot.send_message(chat_id, "⏰ Time up!")
    await send_question(chat_id, context, uid)


# =====================================================
# ⭐ QUIZ FLOW
# =====================================================

# Step 1 → show size options
async def quiz(update, context):
    query = update.callback_query
    await query.answer()

    kb = [
        [InlineKeyboardButton("20 Questions", callback_data="set_20")],
        [InlineKeyboardButton("50 Questions", callback_data="set_50")],
        [InlineKeyboardButton("100 Questions", callback_data="set_100")]
    ]

    await query.message.reply_text(
        "Choose Quiz Length:",
        reply_markup=InlineKeyboardMarkup(kb)
    )


# Step 2 → size selected
async def set_quiz_size(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    username = query.from_user.first_name

    size = int(query.data.split("_")[1])
    quiz_size_store[uid] = size

    # start quiz
    quiz_active[uid] = True
    start_user(uid, username)

    await query.message.reply_text(f"✅ Quiz started with {size} questions!")
    await send_question(query.message.chat_id, context, uid)


# ---------- START ----------
async def start(update, context):
    kb = [
        [InlineKeyboardButton("▶️ Start Quiz", callback_data="startquiz")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="showleader")]
    ]

    await update.message.reply_text(
        "👋 Welcome to GK Quiz Bot!",
        reply_markup=InlineKeyboardMarkup(kb)
    )


# ---------- ANSWER ----------
async def answer(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if not quiz_active.get(uid, False):
        return

    # remove timer
    for job in context.job_queue.get_jobs_by_name(str(uid)):
        job.schedule_removal()

    # prevent double click
    try:
        await query.edit_message_reply_markup(None)
    except:
        pass

    chosen = int(query.data.split("_")[1])
    right, correct = answer_question(uid, chosen)

    if correct is None:
        return

    text = "✅ Correct!" if right else f"❌ Wrong!\nCorrect: {correct}"
    await query.message.reply_text(text)

    await send_question(query.message.chat_id, context, uid)


# ---------- STOP ----------
async def stop(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    quiz_active[uid] = False

    for job in context.job_queue.get_jobs_by_name(str(uid)):
        job.schedule_removal()

    await query.message.reply_text("⛔ Quiz stopped.")


# ---------- RESTART ----------
async def restart(update, context):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    username = query.from_user.first_name

    start_user(uid, username)
    quiz_active[uid] = True

    await send_question(query.message.chat_id, context, uid)


# ---------- RESET ----------
async def reset(update, context):
    uid = update.effective_user.id
    reset_user(uid)
    await update.message.reply_text("🔄 Quiz reset!")


# ---------- LEADERBOARD ----------
async def show_leaderboard(update, context):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(get_leaderboard())
    else:
        await update.message.reply_text(get_leaderboard())
