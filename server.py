
from mcp.server.fastmcp import FastMCP
import sqlite3
from pathlib import Path

mcp = FastMCP("AlexaPlusPlus")

DB_PATH = Path(__file__).with_name("tasks.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'completed'))
            )
        """)


@mcp.tool()
def create_task(title: str) -> dict:
    """Create and save a new task."""
    title = title.strip()

    if not title:
        return {"success": False, "message": "Task title cannot be empty."}

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title) VALUES (?)", (title,)
        )
        task_id = cursor.lastrowid

    return {
        "success": True,
        "id": task_id,
        "title": title,
        "status": "pending"
    }


@mcp.tool()
def list_tasks() -> list[dict]:
    """List all saved tasks."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, title, status FROM tasks ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]


@mcp.tool()
def complete_task(task_id: int) -> dict:
    """Mark a task as completed."""
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET status = 'completed' WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return {"success": False, "message": "Task not found."}

    return {"success": True, "task_id": task_id, "status": "completed"}

     
@mcp.tool()
def clear_completed_tasks() -> dict:
    """Delete all completed tasks."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE status = 'completed'"
        )
        deleted_count = cursor.rowcount

    return {
        "success": True,
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} completed task(s)."
    }

initialize_database()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
