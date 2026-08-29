import sys
from pathlib import Path
from datetime import datetime, timedelta

from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# PATHS & CONFIGURATION
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Allow Python to import files from backend/
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Google Calendar permission scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# OAuth credential files
CREDENTIALS_FILE = BACKEND_DIR / "credentials.json"
TOKEN_FILE = BACKEND_DIR / "calendar_token.json"


# MCP SERVER
mcp = FastMCP("Calendar Server")

# GOOGLE CALENDAR SERVICE
def get_calendar_service():
    credentials = None

    # Load existing token
    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or create new token if invalid
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            credentials = flow.run_local_server(port=8080)

        TOKEN_FILE.write_text(credentials.to_json())

    return build("calendar", "v3", credentials=credentials)


# TOOLS
@mcp.tool()
def list_events() -> str:
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"

        result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = result.get("items", [])
        if not events:
            return "You have no upcoming calendar events."

        output = []
        for event in events:
            title = event.get("summary", "Untitled event")
            start = event["start"].get("dateTime", event["start"].get("date"))
            output.append(f"{title} - {start}")

        return "\n".join(output)

    except Exception as e:
        return f"Calendar error: {e}"


@mcp.tool()
def create_event(title: str, start_time: str, duration_minutes: int = 60) -> str:
    try:
        service = get_calendar_service()

        # Parse start time
        start = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end = start + timedelta(minutes=duration_minutes)

        event = {
            "summary": title,
            "start": {"dateTime": start.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end.isoformat(), "timeZone": "Asia/Kolkata"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        event_link = created_event.get("htmlLink", "")

        return (
            f"Event created successfully.\n"
            f"Title: {title}\n"
            f"Start: {start_time}\n"
            f"Duration: {duration_minutes} minutes\n"
            f"Calendar link: {event_link}"
        )

    except ValueError:
        return "Invalid date/time format. Use YYYY-MM-DD HH:MM."
    except Exception as e:
        return f"Could not create event: {e}"


@mcp.tool()
def delete_event(event_id: str) -> str:
    """
    Delete an event from Google Calendar.
    The event_id can be obtained from the Google Calendar API.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return "Calendar event deleted successfully."
    except Exception as e:
        return f"Could not delete event: {e}"


# MAIN ENTRY POINT
if __name__ == "__main__":
    mcp.run()
