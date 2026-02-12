import json

def load_questions():
    with open("data/questions.json", encoding="utf-8") as f:

        return json.load(f)
