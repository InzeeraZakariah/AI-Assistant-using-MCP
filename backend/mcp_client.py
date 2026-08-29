import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Client for managing connections to multiple MCP servers."""

    def __init__(self):
        # Backend directory
        self.backend_dir = Path(__file__).resolve().parent

        # MCP server files
        self.servers = {
            "calendar": self.backend_dir / "mcp_servers" / "calendar_server.py",
            "tasks": self.backend_dir / "mcp_servers" / "tasks_server.py",
            "weather": self.backend_dir / "mcp_servers" / "weather_server.py",
        }

        # Active sessions and contexts
        self.sessions = {}
        self.contexts = {}

    # ============================================================
    # CONNECT TO MCP SERVERS
    # ============================================================
    async def connect(self):
        """Connect to all MCP servers."""
        print("\nConnecting to MCP servers...")

        for name, server_file in self.servers.items():
            print(f"\nConnecting to MCP server: {name}")
            print(f"File: {server_file}")

            if not server_file.exists():
                print(f"FAILED: {name} server file not found")
                continue

            try:
                server_params = StdioServerParameters(
                    command=sys.executable,
                    args=[str(server_file)]
                )

                # Start MCP server
                context = stdio_client(server_params)
                read_stream, write_stream = await context.__aenter__()

                # Create MCP session
                session = ClientSession(read_stream, write_stream)
                await session.__aenter__()

                # Initialize MCP connection
                await session.initialize()

                # Store session and context
                self.sessions[name] = session
                self.contexts[name] = context

                print(f"CONNECTED: {name} MCP server")

            except Exception as e:
                print(f"FAILED: {name} MCP server")
                print(f"ERROR: {type(e).__name__}: {e}")

    # ============================================================
    # LIST TOOLS
    # ============================================================
    async def list_tools(self):
        """List all available tools from connected MCP servers."""
        all_tools = []

        for server_name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                for tool in result.tools:
                    all_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "server": server_name,
                        "input_schema": tool.inputSchema
                    })
            except Exception as e:
                print(f"Could not get tools from {server_name}: {e}")

        return all_tools

    # ============================================================
    # CALL TOOL
    # ============================================================
    async def call_tool(self, tool_name, arguments):
        """Call a specific MCP tool by name with arguments."""
        for server_name, session in self.sessions.items():
            try:
                result = await session.list_tools()
                tool_found = False

                for tool in result.tools:
                    if tool.name == tool_name:
                        tool_found = True
                        print(f"\nCalling tool: {tool_name}")
                        print(f"Server: {server_name}")
                        print(f"Arguments: {arguments}")

                        result = await session.call_tool(tool_name, arguments)
                        return result

                if not tool_found:
                    continue

            except Exception as e:
                print(f"Error calling {tool_name} on {server_name}: {e}")
                continue

        print(f"Tool not found: {tool_name}")
        return None

    # ============================================================
    # DISCONNECT
    # ============================================================
    async def disconnect(self):
        """Disconnect from all MCP servers."""
        print("\nDisconnecting MCP servers...")

        # Close sessions
        for server_name, session in list(self.sessions.items()):
            try:
                await session.__aexit__(None, None, None)
                print(f"Disconnected: {server_name}")
            except Exception as e:
                print(f"Error disconnecting {server_name}: {e}")

        # Close contexts
        for server_name, context in list(self.contexts.items()):
            try:
                await context.__aexit__(None, None, None)
            except Exception as e:
                print(f"Error closing {server_name}: {e}")

        self.sessions.clear()
        self.contexts.clear()
        print("All MCP servers disconnected.")
