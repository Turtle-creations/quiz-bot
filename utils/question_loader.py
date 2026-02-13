import json
import os
import time

QUESTIONS = []
_last_modified = 0

FILE_PATH = "data/questions.json"   # adjust if path different


def load_questions():
    global QUESTIONS, _last_modified

    if not os.path.exists(FILE_PATH):
        print("[QuestionLoader] File not found")
        QUESTIONS = []
        return QUESTIONS

    modified = os.path.getmtime(FILE_PATH)

    # reload only if changed
    if modified != _last_modified:
        print("[QuestionLoader] Reloading questions...")
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            QUESTIONS = json.load(f)

        _last_modified = modified
        print(f"[QuestionLoader] Loaded {len(QUESTIONS)} questions")

    return QUESTIONS
