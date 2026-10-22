
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import streamlit as st


# -----------------------------
# Alexa++ page configuration
# -----------------------------
st.set_page_config(
    page_title="Alexa++",
    page_icon="✨",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Alexa++ dark purple theme */
    .stApp {
        background: linear-gradient(
            135deg,
            #0b0b14 0%,
            #111126 55%,
            #1a1030 100%
        );
        color: #f5f3ff;
    }

    [data-testid="stSidebar"] {
        background-color: #0e0e1b;
        border-right: 1px solid #29213f;
    }

    [data-testid="stMetric"] {
        background: rgba(139, 92, 246, 0.10);
        border: 1px solid rgba(167, 139, 250, 0.25);
        padding: 18px;
        border-radius: 16px;
    }

/* Subtle styling for task containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: rgba(167, 139, 250, 0.22);
    border-radius: 14px;
}

/* Softer divider lines */
hr {
    border-color: rgba(167, 139, 250, 0.18);
}

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(90deg, #7c3aed, #a855f7);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        border: 1px solid #c4b5fd;
        box-shadow: 0 0 16px rgba(168, 85, 247, 0.35);
        color: white;
    }

    input, textarea {
        border-radius: 10px !important;
    }

    h1, h2, h3 {
        color: #ede9fe;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


# -----------------------------
# MCP connection and tool calls
# -----------------------------
async def _call_mcp_tool(tool_name, arguments=None):
    async with streamablehttp_client(MCP_SERVER_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments or {},
            )

            if result.isError:
                messages = [
                    item.text
                    for item in result.content
                    if hasattr(item, "text")
                ]
                raise RuntimeError(
                    "\n".join(messages) or "The MCP tool failed."
                )

            data = getattr(result, "structuredContent", None)

            if data is not None:
                if isinstance(data, dict) and "result" in data:
                    return data["result"]
                return data

            # Fallback for tools returning text content
            for item in result.content:
                if hasattr(item, "text"):
                    import json
                    return json.loads(item.text)

            return None


def call_mcp_tool(tool_name, arguments=None):
    return asyncio.run(_call_mcp_tool(tool_name, arguments))


def get_tasks():
    result = call_mcp_tool("list_tasks")

    if not isinstance(result, list):
        raise RuntimeError("Unexpected response from list_tasks.")

    return result


def add_task(title):
    title = title.strip()

    if not title:
        return {"success": False, "message": "Please enter a task name."}

    result = call_mcp_tool("create_task", {"title": title})

    if not isinstance(result, dict):
        return {"success": False, "message": "Unexpected server response."}

    return result


def finish_task(task_id):
    result = call_mcp_tool(
        "complete_task",
        {"task_id": int(task_id)},
    )

    if not isinstance(result, dict):
        return {"success": False, "message": "Unexpected server response."}

    return result


# -----------------------------
# Natural-language command handler
# -----------------------------
def handle_command(command):
    command = command.strip()
    lower = command.lower()

    if not command:
        return "Please enter a command."

    if lower in ("show my tasks", "list tasks", "show tasks"):
        tasks = get_tasks()

        if not tasks:
            return "You don't have any tasks yet."

        lines = [
            f"{task['id']}. {task['title']} — {task['status']}"
            for task in tasks
        ]

        return "Here are your tasks:\n" + "\n".join(lines)

    for prefix in ("add task ", "create task "):
        if lower.startswith(prefix):
            title = command[len(prefix):].strip()
            result = add_task(title)

            if result.get("success"):
                return f"Task added: {title}"

            return result.get("message", "Could not add the task.")

    prefix = "remind me to "
    if lower.startswith(prefix):
        title = command[len(prefix):].strip()
        result = add_task(title)

        if result.get("success"):
            return f"Task saved: {title}"

        return result.get("message", "Could not save the task.")

    prefix = "complete task "
    if lower.startswith(prefix):
        task_number = lower[len(prefix):].strip()

        if not task_number.isdigit():
            return "Use a task number, for example: Complete task 2"

        result = finish_task(int(task_number))

        if result.get("success"):
            return f"Task {task_number} marked as completed."

        return result.get("message", "Could not complete that task.")
    
    if lower in ("clear completed tasks", "delete completed tasks"):
        st.session_state["confirm_clear_completed"] = True
        return (
            "Are you sure you want to delete all completed tasks? "
            "Type 'confirm clear completed tasks' to proceed, "
            "or 'cancel clear' to keep them."
        )

    if lower == "cancel clear":
        st.session_state["confirm_clear_completed"] = False
        return "Cancelled. Your completed tasks have been kept."

    if lower == "confirm clear completed tasks":
        if not st.session_state.get("confirm_clear_completed", False):
            return "No deletion is awaiting confirmation."

        result = call_mcp_tool("clear_completed_tasks", {})
        st.session_state["confirm_clear_completed"] = False

        if result.get("success"):
            count = result.get("deleted_count", 0)
            return f"Cleared {count} completed task(s)."

        return result.get("message", "Could not clear completed tasks.")

    return (
        "I don't know that command yet. Try: "
        "'Add task study Python', 'Show my tasks', "
        "or 'Complete task 2'."
    )


# -----------------------------
# Dashboard
# -----------------------------

st.markdown(
    """
    <div style="
        padding: 28px 30px;
        border-radius: 20px;
        background: linear-gradient(
            120deg,
            rgba(124, 58, 237, 0.25),
            rgba(168, 85, 247, 0.08)
        );
        border: 1px solid rgba(167, 139, 250, 0.28);
        margin-bottom: 24px;
    ">
        <div style="
            color: #c4b5fd;
            font-size: 13px;
            letter-spacing: 3px;
            font-weight: 700;
        ">YOUR PERSONAL AI WORKSPACE</div>
        <h1 style="
            color: #f5f3ff;
            font-size: 42px;
            margin: 10px 0 6px 0;
        ">✨ Alexa++</h1>
        <p style="
            color: #c4c0d9;
            font-size: 16px;
            margin: 0;
        ">Organize your tasks. Focus on what matters.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



st.markdown(
    """
    <div style="margin: 20px 0 18px 0;">
        <p style="
            color: #c4b5fd;
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 6px;
        ">YOUR DAY, YOUR MOMENTUM</p>
        <h2 style="
            color: #f5f3ff;
            font-size: 27px;
            margin: 0 0 8px 0;
        ">What are we working on today?</h2>
        <p style="
            color: #a5a0bd;
            font-size: 15px;
            margin: 0;
        ">Give Alexa++ a command, and let's make progress.</p>
    </div>
    """,
    unsafe_allow_html=True,
)



st.markdown("#### 💬 Talk to Alexa++")

st.caption(
    "Enter a command below to manage your tasks."
)

with st.form("assistant_form", clear_on_submit=True):
    command = st.text_input(
        "Your command",
        placeholder="✨  Try: Add task study Python",
        help="Examples: Show my tasks, Add task study Python, Complete task 2",
    )

    command_submitted = st.form_submit_button(
        "✦ Run command",
        use_container_width=True,
    )


if command_submitted:
    try:
        st.session_state["command_result"] = handle_command(command)
    except Exception as error:
        st.session_state["command_result"] = (
            f"Could not contact the MCP server: {error}"
        )

if "command_result" in st.session_state:
    st.info(st.session_state["command_result"])

st.divider()
st.markdown("### Add a task directly")

with st.form("task_form", clear_on_submit=True):
    title = st.text_input(
        "Task name",
        placeholder="e.g. Study DBMS",
    )
    task_submitted = st.form_submit_button("＋ Add task")

if task_submitted:
    try:
        result = add_task(title)

        if result.get("success"):
            st.session_state["command_result"] = (
                f"Task added: {title.strip()}"
            )
            st.rerun()
        else:
            st.warning(result.get("message", "Could not add the task."))
    except Exception as error:
        st.error(f"Could not contact the MCP server: {error}")

st.divider()

st.markdown(
    """
    <div style="margin: 28px 0 16px 0;">
        <h2 style="color: #ede9fe; margin-bottom: 4px;">
            📋 Your Task Space
        </h2>
        <p style="color: #a5a0bd; font-size: 14px;">
            Keep track of your priorities and celebrate your progress.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


try:
    tasks = get_tasks()

    completed = sum(
        task["status"] == "completed" for task in tasks
    )
    total = len(tasks)
    pending = total - completed
    progress = completed / total if total > 0 else 0

    st.markdown("#### 🎯 Your Progress")
    st.progress(progress)
    st.caption(f"{completed} of {total} tasks completed")

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.metric("📋 Total Tasks", total, border=True)

    with col2:
        st.metric("⏳ Pending", pending, border=True)

    with col3:
        st.metric("✅ Completed", completed, border=True)

    st.progress(completed / total if total else 0)

    if not tasks:
        st.info("No tasks yet. Add your first task above!")
    else:
        task_filter = st.selectbox(
    "Filter tasks",
    ["All Tasks", "Pending", "Completed"],
)

        for task in tasks:
              task_id = task["id"]
              title = task["title"]
              status = task["status"]

            
              col1, col2 = st.columns([5, 1])

              with col1:
                     if status == "completed":
                       st.markdown(
                           f"✅ **#{task_id} — {title}**  \n"
                           f"Status: 🟢 Completed"
                       )
                     else:
                        st.markdown(
                        f"📌 **#{task_id} — {title}**  \n"
                        f"Status: 🟡 Pending"
                    )


              with col2:
                if status == "pending":
                    if st.button("Complete", key=f"task_{task_id}"):
                        try:
                            result = finish_task(task_id)

                            if result.get("success"):
                                st.session_state["command_result"] = (
                                    f"Task {task_id} completed."
                                )
                                st.rerun()
                            else:
                                st.warning(
                                    result.get(
                                        "message",
                                        "Could not complete the task.",
                                    )
                                )
                        except Exception as error:
                            st.error(f"Could not contact MCP: {error}")
                else:
                    st.caption("Done")

except Exception as error:
    st.error(
        "Alexa++ could not load tasks from MCP. "
        "Make sure server.py is running on port 8000."
    )
    st.caption(str(error))

st.divider()

with st.sidebar:
    st.markdown("## ✨ Alexa++")
    st.caption("YOUR AI WORKSPACE")
    st.divider()

    st.markdown("### Navigation")
    st.markdown("🏠  Dashboard")
    st.markdown("📋  My Tasks")
    st.markdown("⚙️  Settings")

    st.divider()
    st.markdown("### System Status")
    st.success("MCP tools connected")
    st.caption("Local task server")

st.caption("Alexa++ | Powered by MCP task tools")
