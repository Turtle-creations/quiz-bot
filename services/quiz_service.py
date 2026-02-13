import json
import random
import os

# ================= LOAD QUESTIONS =================
QUESTIONS = []

def load_questions():
    global QUESTIONS
    try:
        with open("data/questions.json", "r", encoding="utf-8") as f:
            QUESTIONS = json.load(f)
        print(f"[Quiz] Loaded {len(QUESTIONS)} questions")
    except Exception as e:
        print("[Quiz] Failed to load questions:", e)
        QUESTIONS = []

# First load on startup
load_questions()


# ================= CONFIG =================
SET_SIZE = 100

score = {}
index = {}
order = {}
username_store = {}
leaderboard = {}
answered_flag = {}


# ================= USER START =================
def start_user(uid, username=None, set_size=None):
    if not QUESTIONS:
        return

    username_store[uid] = username or str(uid)

    score[uid] = 0
    index[uid] = 0
    answered_flag[uid] = False

    size = set_size or SET_SIZE
    size = min(size, len(QUESTIONS))

    order[uid] = random.sample(range(len(QUESTIONS)), size)


# ================= GET QUESTION =================
def get_question(uid):
    if uid not in index:
        return None

    if index[uid] >= len(order.get(uid, [])):
        return None

    answered_flag[uid] = False
    return QUESTIONS[order[uid][index[uid]]]


# ================= ANSWER =================
def answer_question(uid, chosen):

    if answered_flag.get(uid, False):
        return False, None

    if uid not in order or index[uid] >= len(order[uid]):
        return False, None

    answered_flag[uid] = True

    qdata = QUESTIONS[order[uid][index[uid]]]
    correct = qdata["answer"]

    right = chosen == correct
    if right:
        score[uid] += 1

    index[uid] += 1
    return right, qdata["options"][correct]


# ================= SKIP =================
def skip_question(uid):
    if uid in index:
        index[uid] += 1


# ================= SCORE =================
def get_score(uid):
    return score.get(uid, 0), len(order.get(uid, []))


# ================= LEADERBOARD =================
def update_leaderboard(uid):
    s, total = get_score(uid)

    leaderboard[uid] = {
        "name": username_store.get(uid, str(uid)),
        "score": s,
        "total": total,
    }


def get_leaderboard():
    if not leaderboard:
        return "🏆 Leaderboard\n\nNo players yet."

    users = sorted(
        leaderboard.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    text = "🏆 Leaderboard\n\n"
    for i, u in enumerate(users[:10], 1):
        text += f"{i}. {u['name']} — {u['score']}/{u['total']}\n"

    return text


# ================= RESET =================
def reset_user(uid):
    score.pop(uid, None)
    index.pop(uid, None)
    order.pop(uid, None)
    answered_flag.pop(uid, None)
    username_store.pop(uid, None)
    leaderboard.pop(uid, None)


# ================= RELOAD SUPPORT ⭐ =================
def reload_questions():
    load_questions()
    return f"✅ Reloaded {len(QUESTIONS)} questions!"
