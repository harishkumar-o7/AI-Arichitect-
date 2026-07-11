import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "ai_architect.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            plan_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON saved_plans (user_id)
    """)
    conn.commit()
    conn.close()


def save_plan(user_id, plan_data, title=None):
    if not title:
        title = f"{plan_data.get('bedrooms', '?')}BHK - {plan_data.get('area', '?')} sqft"

    conn = _connect()
    cursor = conn.execute(
        "INSERT INTO saved_plans (user_id, title, plan_data, created_at) VALUES (?, ?, ?, ?)",
        (user_id, title, json.dumps(plan_data), datetime.utcnow().isoformat())
    )
    conn.commit()
    plan_id = cursor.lastrowid
    conn.close()
    return plan_id


def get_history(user_id):
    conn = _connect()
    rows = conn.execute(
        "SELECT id, user_id, title, created_at FROM saved_plans WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_plan(plan_id, user_id=None):
    conn = _connect()
    if user_id:
        row = conn.execute(
            "SELECT * FROM saved_plans WHERE id = ? AND user_id = ?",
            (plan_id, user_id)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM saved_plans WHERE id = ?",
            (plan_id,)
        ).fetchone()
    conn.close()

    if not row:
        return None

    result = dict(row)
    result["plan_data"] = json.loads(result["plan_data"])
    return result


def delete_plan(plan_id, user_id):
    conn = _connect()
    cursor = conn.execute(
        "DELETE FROM saved_plans WHERE id = ? AND user_id = ?",
        (plan_id, user_id)
    )
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
