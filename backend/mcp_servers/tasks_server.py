import sys
from pathlib import Path

from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Find the backend folder
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Add backend/ to Python's import path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Google Tasks permission scopes
SCOPES = ["https://www.googleapis.com/auth/tasks"]

# OAuth credential files
CREDENTIALS_FILE = BACKEND_DIR / "credentials.json"
TOKEN_FILE = BACKEND_DIR / "tasks_token.json"


mcp = FastMCP("Tasks Server")

def get_tasks_service():
    """
    Authenticate and return a Google Tasks service instance.
    Handles token refresh and OAuth login if needed.
    """
    credentials = None

    # Load existing token
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or create new token if invalid
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            credentials = flow.run_local_server(port=8080)

        TOKEN_FILE.write_text(credentials.to_json())

    return build("tasks", "v1", credentials=credentials)


def get_task_list(service):
    """
    Retrieve the first available Google Task list.
    """
    result = service.tasklists().list().execute()
    task_lists = result.get("items", [])
    if not task_lists:
        return None
    return task_lists[0]["id"]


@mcp.tool()
def list_tasks() -> str:
    """
    List pending tasks from Google Tasks.
    """
    try:
        service = get_tasks_service()
        task_list_id = get_task_list(service)
        if not task_list_id:
            return "No Google Task list found."

        result = service.tasks().list(
            tasklist=task_list_id,
            showCompleted=False,
            showHidden=False
        ).execute()

        tasks = result.get("items", [])
        if not tasks:
            return "You have no pending tasks."

        output = [f"{task.get('title', 'Untitled task')} | ID: {task.get('id', '')}" for task in tasks]
        return "\n".join(output)

    except Exception as e:
        return f"Tasks error: {e}"


@mcp.tool()
def create_task(title: str) -> str:
    """
    Create a new task in Google Tasks.
    """
    try:
        service = get_tasks_service()
        task_list_id = get_task_list(service)
        if not task_list_id:
            return "No Google Task list found."

        task = {"title": title}
        created_task = service.tasks().insert(tasklist=task_list_id, body=task).execute()
        task_id = created_task.get("id", "")

        return (
            f"Task created successfully.\n"
            f"Title: {title}\n"
            f"Task ID: {task_id}"
        )

    except Exception as e:
        return f"Could not create task: {e}"


@mcp.tool()
def complete_task(task_id: str) -> str:
    """
    Mark a Google Task as completed.
    """
    try:
        service = get_tasks_service()
        task_list_id = get_task_list(service)
        if not task_list_id:
            return "No Google Task list found."

        service.tasks().patch(
            tasklist=task_list_id,
            task=task_id,
            body={"status": "completed"}
        ).execute()

        return "Task completed successfully."

    except Exception as e:
        return f"Could not complete task: {e}"


if __name__ == "__main__":
    mcp.run()
