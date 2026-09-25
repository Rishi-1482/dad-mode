import sqlite3
from pathlib import Path


DB_PATH = Path("data/memory.db")


def init_logs():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                route TEXT,
                tools TEXT,
                latency_ms REAL,
                success INTEGER,
                model TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                estimated_cost REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP

            )
            """
        )

        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(request_logs)")
        }

        if "estimated_cost" not in columns:
            conn.execute(
                "ALTER TABLE request_logs "
                "ADD COLUMN estimated_cost REAL DEFAULT 0.0"
            )

        conn.commit()


def log_request(
    conversation_id: str,
    route: str,
    tools: list[str],
    latency_ms: float,
    success: bool,
    model: str = "",
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost: float = 0.0,
):
    init_logs()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO request_logs (
                conversation_id,
                route,
                tools,
                latency_ms,
                success,
                model,
                input_tokens,
                output_tokens,
                estimated_cost
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                route,
                ",".join(tools),
                latency_ms,
                int(success),
                model,
                input_tokens,
                output_tokens,
                estimated_cost,
            ),
        )

        conn.commit()