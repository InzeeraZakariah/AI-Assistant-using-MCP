# AI Personal Assistant using MCP

An AI-powered personal assistant that uses **Groq LLM** and the **Model Context Protocol (MCP)** to interact with external services such as Google Calendar, Google Tasks, and Weather APIs.

The user communicates with the assistant through a simple web interface. The Groq LLM understands the user's request, selects the appropriate MCP tool, and the MCP client communicates with the corresponding MCP server.

## Features

* Natural language interaction with an AI assistant
* LLM-based tool selection using Groq
* MCP-based architecture
* Google Calendar integration
* Google Tasks integration
* Weather information
* Create and list Google Tasks
* Complete Google Tasks
* List and manage calendar events
* Simple HTML/CSS/JavaScript frontend
* FastAPI backend
* Multiple independent MCP servers
* Dynamic MCP tool discovery

## Technologies Used

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* FastAPI
* Uvicorn

### AI

* Groq
* openai/gpt-oss-120b

### MCP

* FastMCP
* MCP Python SDK
* MCP Client
* MCP Servers
* stdio transport

### APIs

* Google Calendar API
* Google Tasks API
* Open-Meteo Weather API

## System Architecture

```text
                         USER
                           |
                           v
                  HTML / CSS / JS
                     Frontend
                           |
                           | HTTP
                           v
                    FastAPI Backend
                       main.py
                           |
                           v
                     Assistant
                     assistant.py
                           |
                           v
                       Groq LLM
                           |
                 Understands request
                           |
                 Selects MCP tool
                           |
                           v
                     MCP Client
                   mcp_client.py
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       Calendar MCP    Tasks MCP     Weather MCP
          Server          Server         Server
             |             |             |
             v             v             v
       Google Calendar  Google Tasks  Open-Meteo
```

## How the Application Works

The application follows these steps:

1. The user enters a natural language request in the frontend.
2. JavaScript sends the request to the FastAPI backend.
3. FastAPI passes the request to `assistant.py`.
4. The assistant sends the request and available MCP tools to the Groq LLM.
5. Groq understands the user's intention.
6. Groq selects the appropriate MCP tool.
7. The MCP client finds the selected tool.
8. The MCP client calls the corresponding MCP server.
9. The MCP server communicates with the external service.
10. The result is returned to the MCP client.
11. The assistant sends the result to Groq.
12. Groq converts the result into a natural-language response.
13. FastAPI returns the response to the frontend.
14. The frontend displays the response to the user.

## Example

User:

```text
What is the weather in Chennai?
```

The Groq LLM identifies:

```text
Tool: get_weather
Arguments:
{
    "location": "Chennai"
}
```

The MCP client calls:

```text
weather_server.py
```

The Weather MCP server gets information from the weather API and returns the result.

The assistant then generates a response such as:

```text
The current weather in Chennai is 32°C with clear skies.
```

## Project Structure

```text
AI Personal Assistant using MCP/
│
├── backend/
│   │
│   ├── main.py
│   ├── assistant.py
│   ├── mcp_client.py
│   ├── credentials.json
│   ├── tasks_token.json
│   ├── calendar_token.json
│   │
│   └── mcp_servers/
│       ├── calendar_server.py
│       ├── tasks_server.py
│       └── weather_server.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## File Description

### `backend/main.py`

The main FastAPI application.

It:

* Starts the FastAPI server
* Initializes the AI assistant
* Provides the `/chat` endpoint
* Receives messages from the frontend
* Sends responses back to the frontend
* Handles application startup and shutdown

### `backend/assistant.py`

The main AI logic.

It:

* Connects to the MCP client
* Gets the available MCP tools
* Sends the tools to the Groq LLM
* Understands the user's request
* Allows the LLM to select the appropriate tool
* Sends arguments to the selected MCP tool
* Processes the tool result
* Generates the final natural-language response

### `backend/mcp_client.py`

The MCP client manages connections to all MCP servers.

It:

* Starts MCP servers using stdio
* Creates MCP sessions
* Discovers available tools
* Calls MCP tools
* Manages MCP server connections
* Disconnects from MCP servers when the application shuts down

### `calendar_server.py`

The Calendar MCP server.

It provides tools for interacting with Google Calendar.

Example tools:

```text
list_events
create_event
delete_event
```

### `tasks_server.py`

The Tasks MCP server.

It provides tools for interacting with Google Tasks.

Example tools:

```text
list_tasks
create_task
complete_task
```

### `weather_server.py`

The Weather MCP server.

It provides weather-related tools.

Example:

```text
get_weather
```

The server communicates with the weather API to retrieve weather information.

### `frontend/index.html`

Contains the structure of the web application.

It provides:

* Chat interface
* Message input
* Send button
* Tool information
* Suggested questions
* Connection status

### `frontend/style.css`

Contains the styling for the web application.

### `frontend/app.js`

Handles frontend-backend communication.

It:

* Sends user messages to FastAPI
* Receives assistant responses
* Displays messages
* Shows loading status
* Checks backend connectivity

## Installation

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
```

Move into the project:

```bash
cd "AI Personal Assistant using MCP"
```

## 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```



## 4. Configure Groq

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
```

Never commit your API key to GitHub.

In `assistant.py`, load the environment variables:

```python
from dotenv import load_dotenv

load_dotenv()
```

Then:

```python
import os

api_key = os.getenv("GROQ_API_KEY")
```

## 5. Configure Google APIs

The application uses Google Calendar and Google Tasks.

In Google Cloud Console:

1. Create or select a Google Cloud project.
2. Enable Google Calendar API.
3. Enable Google Tasks API.
4. Configure the OAuth consent screen.
5. Create an OAuth client.
6. Use a Desktop application OAuth client for the local Python application.
7. Download the credentials file.
8. Rename it to:

```text
credentials.json
```

9. Place it inside:

```text
backend/credentials.json
```

## Google OAuth Scopes

### Google Calendar

Use the scope required by your Calendar server, for example:

```text
https://www.googleapis.com/auth/calendar
```

### Google Tasks

```text
https://www.googleapis.com/auth/tasks
```

Only request the scopes that your application actually uses.

## 6. Google Authentication

The first time you use Google Calendar or Google Tasks, Google will ask you to authorize the application.

After successful authentication, token files are generated.

For example:

```text
backend/
├── credentials.json
├── calendar_token.json
└── tasks_token.json
```

These token files should not be uploaded to GitHub.

## 7. Run the Backend

Move into the backend directory:

```powershell
cd backend
```

Start FastAPI:

```powershell
uvicorn main:app --reload
```

The backend will normally run at:

```text
http://127.0.0.1:8000
```

You can test the backend using:

```text
http://127.0.0.1:8000/
```

## 8. Run the Frontend

Open:

```text
frontend/index.html
```

in your browser.

For a better development setup, you can use VS Code Live Server.

The frontend communicates with:

```text
http://127.0.0.1:8000
```

## API Endpoint

### `GET /`

Checks whether the backend is running.

Example response:

```json
{
    "status": "AI Personal Assistant is running"
}
```

### `POST /chat`

Sends a user message to the assistant.

Request:

```json
{
    "message": "Show my tasks"
}
```

Response:

```json
{
    "response": "You have 3 pending tasks."
}
```

## MCP Tool Flow

The application does not use hard-coded keyword matching.

Instead, the LLM decides which tool should be used.

For example:

```text
User:
"Add a task to complete my project report"
```

Groq understands the request and selects:

```text
create_task
```

with:

```json
{
    "title": "Complete my project report"
}
```

The MCP client then calls:

```text
tasks_server.py
```

The Tasks server communicates with Google Tasks.

## Available MCP Tools

Depending on your current server implementation, tools can include:

### Calendar

```text
list_events
create_event
delete_event
```

### Tasks

```text
list_tasks
create_task
complete_task
```

### Weather

```text
get_weather
```

## Why MCP?

Without MCP, the assistant would need separate integrations directly inside the main application:

```text
Assistant
   |
   +---- Google Calendar code
   |
   +---- Google Tasks code
   |
   +---- Weather API code
```

With MCP:

```text
Assistant
   |
   v
MCP Client
   |
   +---- Calendar MCP Server
   |
   +---- Tasks MCP Server
   |
   +---- Weather MCP Server
```

This separates the AI reasoning layer from the external tools.

## Advantages

* Modular architecture
* Easy to add new tools
* LLM-based tool selection
* External services are isolated in MCP servers
* Easier maintenance
* Reusable MCP tools
* Clear separation between frontend, backend, AI, and tools

## Adding a New Tool

To add another capability:

1. Create a new MCP server.
2. Add tools using FastMCP.
3. Add the server to `mcp_client.py`.
4. Restart the backend.
5. The MCP client discovers the new tools.
6. The Groq assistant can use the new tools.

For example:

```text
mcp_servers/
├── calendar_server.py
├── tasks_server.py
├── weather_server.py
└── notes_server.py
```

The assistant can then discover tools exposed by `notes_server.py`.

## Security

Do not commit the following files:

```text
.env
credentials.json
calendar_token.json
tasks_token.json
```

Add them to `.gitignore`:

```text
.venv/
__pycache__/
.env
credentials.json
calendar_token.json
tasks_token.json
*.pyc
```

## Future Improvements

Possible future features include:

* Gmail integration
* Google Drive integration
* Notes management
* Email sending
* Meeting scheduling
* Reminders
* Location-based weather
* Multi-turn conversations
* Conversation memory
* Voice input
* Voice output
* Authentication
* User-specific accounts
* Better LLM tool calling
* Cloud deployment
* Docker support

## Future Architecture

The application can be extended to:

```text
                         AI PERSONAL ASSISTANT
                                  |
                              Groq LLM
                                  |
                             MCP Client
                                  |
       +------------+-------------+-------------+-------------+
       |            |             |             |             |
       v            v             v             v             v
   Calendar       Tasks        Weather        Gmail         Drive
     MCP           MCP           MCP           MCP           MCP
     Server        Server        Server        Server        Server
       |            |             |             |             |
       v            v             v             v             v
   Google         Google       Weather        Gmail         Google
   Calendar       Tasks         API            API           Drive
```

## Project Goal

The goal of this project is to demonstrate how an LLM can interact with multiple external services through the **Model Context Protocol (MCP)**.

Instead of building separate logic for every possible user command, the LLM understands the user's natural-language request and selects the appropriate MCP tool dynamically.

## Author

**Inzeera Z**

B.Tech (Hons) Artificial Intelligence & Data Science

## License

This project is for educational and demonstration purposes.
