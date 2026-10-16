import re
import sqlite3
from pathlib import Path


# Store memory locally, outside the project source files.
MEMORY_DIRECTORY = Path.home() / "OrizonFiles"
MEMORY_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = MEMORY_DIRECTORY / "orizon_memory.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_memory():
    with get_connection() as connection:

        # Create the memories table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL DEFAULT 'general',
                memory_key TEXT NOT NULL UNIQUE,
                memory_value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create the tasks table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

    print("Orizon memory initialized.")
    
def migrate_memory_keys():
    """Normalize existing keys and merge duplicate entries."""

    memories = list_memories()

    for item in memories:
        old_key = item["memory_key"]
        new_key = normalize_key(old_key)

        if old_key == new_key:
            continue

        existing = recall(new_key)

        if existing:
            # Keep the newer entry's value when merging duplicates.
            with get_connection() as connection:
                connection.execute(
                    "DELETE FROM memories WHERE memory_key = ?",
                    (old_key,)
                )
        else:
            with get_connection() as connection:
                connection.execute(
                    "UPDATE memories SET memory_key = ? WHERE memory_key = ?",
                    (new_key, old_key)
                )

def normalize_key(key):
    key = key.strip().lower()
    key = key.replace("_", " ")
    key = re.sub(r"\s+", " ", key)
    return key
def remember(key, value, category="general"):
    key = normalize_key(key)
    value = value.strip()
    category = category.strip().lower()

    if not key or not value:
        return False

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO memories (
                category,
                memory_key,
                memory_value
            )
            VALUES (?, ?, ?)
            ON CONFLICT(memory_key)
            DO UPDATE SET
                category = excluded.category,
                memory_value = excluded.memory_value
        """, (category, key, value))

    return True


def recall(key):
    key = normalize_key(key)

    with get_connection() as connection:
        row = connection.execute("""
            SELECT memory_key, memory_value, category
            FROM memories
            WHERE memory_key = ?
        """, (key,)).fetchone()

    if row:
        return dict(row)

    return None


def list_memories():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, category, memory_key, memory_value
            FROM memories
            ORDER BY id
        """).fetchall()

    return [dict(row) for row in rows]


def delete_memory(memory_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            DELETE FROM memories
            WHERE id = ?
        """, (memory_id,))

        return cursor.rowcount > 0
def delete_memory_by_key(key):
    key = normalize_key(key)

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM memories WHERE memory_key = ?",
            (key,)
        )

        return cursor.rowcount > 0


def clear_all_memories():
    with get_connection() as connection:
        connection.execute("DELETE FROM memories")
def add_task(title):
    title = title.strip()

    if not title:
        return False

    with get_connection() as connection:
        connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )

    return True


def list_tasks():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, title, status, created_at, completed_at
            FROM tasks
            ORDER BY id
        """).fetchall()

    return [dict(row) for row in rows]


def complete_task(task_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE tasks
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND status = 'pending'
        """, (task_id,))

        return cursor.rowcount > 0


def delete_task(task_id):
    with get_connection() as connection:
        cursor = connection.execute("""
            DELETE FROM tasks
            WHERE id = ?
        """, (task_id,))

        return cursor.rowcount > 0

if __name__ == "__main__":
    initialize_memory()

    print("\n--- ORIZON MEMORY TEST ---")

    remember(
        "favourite_programming_language",
        "Python",
        "preferences"
    )

    print("Memory saved!")

    result = recall("favourite_programming_language")

    if result:
        print("Recalled memory:", result["memory_value"])
    else:
        print("Memory not found!")

    print("\nAll saved memories:")

    for memory in list_memories():
        print(
            f'{memory["id"]}. '
            f'{memory["memory_key"]} = '
            f'{memory["memory_value"]}'
        )