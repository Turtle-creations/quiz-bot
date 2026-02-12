import sqlite3
from pathlib import Path

DB_PATH = Path("quiz.db")


# Connection create
def get_connection():
    return sqlite3.connect(DB_PATH)


# Table create (first run)
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        score INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# Score update / insert
def update_score(user_id, username, score):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO leaderboard (user_id, username, score)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id)
    DO UPDATE SET
        username=excluded.username,
        score = score + excluded.score
    """)

    conn.commit()
    conn.close()


# Top users fetch
def get_top_users(limit=5):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT username, score
    FROM leaderboard
    ORDER BY score DESC
    LIMIT ?
    """, (limit,))

    data = cur.fetchall()
    conn.close()
    return data
