# Alexa++ — MCP-Powered Productivity Assistant

Alexa++ is a productivity assistant prototype that helps users organize and manage everyday tasks through a web dashboard. It demonstrates how an application can connect to tools through the **Model Context Protocol (MCP)** using **Streamable HTTP**.

## ✨ Features

- **Create tasks:** Add tasks using the dashboard or supported text commands.
- **View tasks:** Display and review saved tasks.
- **Complete tasks:** Mark tasks as completed.
- **Filter tasks:** Organize tasks by their status.
- **Track progress:** View task statistics and completion progress.
- **Clear completed tasks:** Remove completed tasks with a confirmation step.
- **MCP integration:** Connect a client to an MCP server that exposes task-management tools.
- **Persistent storage:** Store task data locally using SQLite.

## 🛠️ Tech Stack

- Python
- Streamlit
- Model Context Protocol (MCP)
- Streamable HTTP transport
- SQLite
- OpenAI Python SDK (included for experimentation)

## 🏗️ Architecture

1. **Streamlit dashboard:** Provides the user interface.
2. **Command handler:** Interprets supported task commands.
3. **MCP client:** Sends tool calls to the MCP server.
4. **MCP server:** Exposes task-management tools over Streamable HTTP.
5. **SQLite database:** Stores task information locally.

## 🚀 Getting Started

### Prerequisites

- Python installed
- Git
- Visual Studio Code or another code editor

### 1. Clone the repository

```bash
git clone https://github.com/SreehasiniReddy/alexa-plus-plus.git
cd alexa-plus-plus
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the MCP server

Open the first terminal and run:

```powershell
python server.py
```

Keep this terminal running.

### 5. Start the dashboard

Open a second terminal in the project folder, activate the virtual environment if needed, and run:

```powershell
streamlit run app.py
```

Open the local address printed by Streamlit in your browser.

## 🔧 MCP Tools

The MCP server provides task-management tools, including:

- `create_task` — creates a task.
- `list_tasks` — lists saved tasks.
- `complete_task` — marks a task as complete.
- `clear_completed_tasks` — removes completed tasks.

## 🔐 Security Notes

- Never commit `.env` files or API keys.
- Keep `.venv/`, Python cache files, and the local SQLite database out of version control.
- Task data is stored locally in the SQLite database.

## 🎯 Project Goal

Alexa++ explores how MCP and connected tools can support a more useful productivity-assistant experience. Future improvements may include richer natural-language understanding, Agent Skills support, and additional productivity tools.

## 📌 Project Status

**Prototype in development.** Features and integrations are being tested and improved.

## 🔗 Repository

[View Alexa++ on GitHub](https://github.com/SreehasiniReddy/alexa-plus-plus)
