import sqlite3
from pathlib import Path


DB_PATH = Path("data/memory.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()


def save_message(
    conversation_id: str,
    role: str,
    content: str,
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content
            )
            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
            ),
        )

        conn.commit()


def get_recent_messages(
    conversation_id: str,
    limit: int = 8,
) -> list[dict]:

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                conversation_id,
                limit,
            ),
        ).fetchall()

    messages = [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in reversed(rows)
    ]

    return messages


def clear_conversation(
    conversation_id: str,
):
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM messages
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )

        conn.commit()


def init_long_term_memory():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT NOT NULL,
                memory_value TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(memory_key)
            )
            """
        )

        conn.commit()

def save_memory(
    memory_key: str,
    memory_value: str,
    category: str,
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO memories (
                memory_key,
                memory_value,
                category
            )
            VALUES (?, ?, ?)
            ON CONFLICT(memory_key)
            DO UPDATE SET
                memory_value = excluded.memory_value,
                category = excluded.category,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                memory_key,
                memory_value,
                category,
            ),
        )

        conn.commit()


def get_memories(
    limit: int = 20,
) -> list[dict]:

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT
                memory_key,
                memory_value,
                category
            FROM memories
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "key": row["memory_key"],
            "value": row["memory_value"],
            "category": row["category"],
        }
        for row in rows
    ]

init_db()
init_long_term_memory()