import json
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

QUESTION_FILE = Path("data/questions.json")

# Cache
_cache = []
_last_load_time = 0
_reload_interval = 5  # seconds (auto reload check)

def load_questions():
    global _cache, _last_load_time

    try:
        now = time.time()

        # Reload only if time passed
        if now - _last_load_time > _reload_interval:
            with open(QUESTION_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)

            _last_load_time = now
            logger.info(f"[Questions Reloaded] {_last_load_time}")

        return _cache

    except Exception as e:
        logger.exception("Question load crash")
        return _cache

def force_reload():
    global _last_load_time
    _last_load_time = 0
