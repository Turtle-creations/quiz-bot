import json
import uuid

FILE = "data/questions.json"

# Load questions
with open(FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)

updated = False

for q in questions:
    if "id" not in q:
        q["id"] = str(uuid.uuid4())[:8]   # short unique id
        updated = True

# Save back if changed
if updated:
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print("✅ IDs added successfully")
else:
    print("✔ All questions already have IDs")
