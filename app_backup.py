
import sqlite3
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Alexa++",
    page_icon="✨",
    layout="wide",
)

DB_PATH = Path(__file__).with_name("tasks.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_tasks():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, title, status FROM tasks ORDER BY id DESC"
        ).fetchall()


def add_task(title):
    title = title.strip()

    if not title:
        return False

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,),
        )
    return True


def finish_task(task_id):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = 'completed' "
            "WHERE id = ? AND status = 'pending'",
            (task_id,),
        )
        return cursor.rowcount > 0


def handle_command(command):
    command = command.strip()
    lower = command.lower()

    if lower in ("show my tasks", "list tasks", "show tasks"):
        tasks = get_tasks()
        if not tasks:
            return "You don't have any tasks yet."

        lines = [
            f"{t['id']}. {t['title']} — {t['status']}"
            for t in tasks
        ]
        return "Here are your tasks:\n" + "\n".join(lines)

    for prefix in ("add task ", "create task "):
        if lower.startswith(prefix):
            title = command[len(prefix):].strip()
            if add_task(title):
                return f"Task added: {title}"
            return "Please enter a task name."

    if lower.startswith("remind me to "):
        title = command[len("remind me to "):].strip()
        if add_task(title):
            return f"Task saved: {title}"
        return "Please tell me what to remember."

    if lower.startswith("complete task "):
        task_number = lower.removeprefix("complete task ").strip()

        if task_number.isdigit():
            if finish_task(int(task_number)):
                return f"Task {task_number} marked as completed."
            return "I couldn't find that pending task."

        return "Use a task number, for example: Complete task 2"

    return (
        "I don't know that command yet. Try: "
        "'Add task prepare my presentation', "
        "'Show my tasks', or 'Complete task 2'."
    )


st.title("✨ Alexa++")
st.caption("Your personal productivity assistant")

st.markdown("### What can I help you accomplish today?")

with st.form("assistant_form", clear_on_submit=True):
    command = st.text_input(
        "Give Alexa++ a command",
        placeholder="e.g. Add task prepare my presentation",
    )
    submitted = st.form_submit_button("Run command")

    if submitted:
        st.session_state["command_result"] = handle_command(command)

if "command_result" in st.session_state:
    st.info(st.session_state["command_result"])

st.divider()
st.markdown("### Add a task directly")

with st.form("task_form", clear_on_submit=True):
    title = st.text_input(
        "Task name",
        placeholder="e.g. Study DBMS",
    )
    submitted = st.form_submit_button("＋ Add task")

    if submitted:
        if add_task(title):
            st.session_state["command_result"] = f"Task added: {title}"
            st.rerun()
        else:
            st.warning("Please enter a task name.")

tasks = get_tasks()
completed = sum(t["status"] == "completed" for t in tasks)
total = len(tasks)
pending = total - completed

col1, col2, col3 = st.columns(3)
col1.metric("Total tasks", total)
col2.metric("Pending", pending)
col3.metric("Completed", completed)

st.progress(completed / total if total else 0)

st.markdown("### Your tasks")

if not tasks:
    st.info("No tasks yet. Add your first task above!")
else:
    for task in tasks:
        task_id = task["id"]
        title = task["title"]
        status = task["status"]

        col1, col2 = st.columns([5, 1])

        with col1:
            if status == "completed":
                st.write(f"✅ ~~{title}~~")
            else:
                st.write(f"📌 **#{task_id}** {title}")

        with col2:
            if status == "pending":
                if st.button("Complete", key=f"task_{task_id}"):
                    finish_task(task_id)
                    st.rerun()
            else:
                st.caption("Done")

st.divider()
st.caption("Alexa++ | Your tasks are saved locally.")
