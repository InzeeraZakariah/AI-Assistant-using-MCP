import os
import json
from groq import Groq
from mcp_client import MCPClient
from dotenv import load_dotenv

load_dotenv()

class Assistant:
    def __init__(self):
        self.mcp = MCPClient()
        self.tools = []

        # Groq client
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"

        print("Assistant created.")

    # INITIALIZATION & SHUTDOWN
    async def initialize(self):
        """Connect to MCP servers and list available tools."""
        print("Initializing AI Personal Assistant...")
        await self.mcp.connect()
        self.tools = await self.mcp.list_tools()

        print("\nAvailable MCP tools:")
        for tool in self.tools:
            print(f"- {tool['name']} ({tool['server']})")
        print("\nAssistant initialized.")

    async def shutdown(self):
        """Disconnect from MCP servers."""
        print("Shutting down AI Personal Assistant...")
        await self.mcp.disconnect()
        print("Assistant shutdown complete.")

    # PROCESS USER MESSAGE
    async def process(self, message: str):
        """Process user input and decide whether to call an MCP tool or respond directly."""
        message = message.strip()
        if not message:
            return "Please enter a message."

        print(f"\nUser: {message}")

        # Build system prompt with tool descriptions
        tools_description = self.get_tools_description()
        system_prompt = f"""
                        You are an AI Personal Assistant.

                        You can use tools provided by MCP servers.

                        Your job is to understand the user's request
                        and decide whether an MCP tool is required.

                        Available MCP tools:

                        {tools_description}

                        IMPORTANT RULES:
                        1. Use an MCP tool when the user's request requires calendar, tasks, or weather information.
                        2. Do not invent tool names.
                        3. Use only the tools listed above.
                        4. Extract the required arguments from the user's message.
                        5. If a tool is not required, answer normally.
                        6. If a tool is required, return ONLY this JSON format:
                        {{
                            "action": "tool",
                            "tool_name": "TOOL_NAME",
                            "arguments": {{
                                "argument": "value"
                            }}
                        }}
                        7. If no tool is required, return:
                        {{
                            "action": "response",
                            "response": "your answer"
                        }}
                        """

        try:
            # Query Groq LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0
            )

            llm_response = response.choices[0].message.content
            print(f"\nLLM response:\n{llm_response}")

            decision = self.parse_llm_response(llm_response)

            # Normal response
            if decision.get("action") == "response":
                return decision.get("response", "I could not generate a response.")

            # Tool call
            if decision.get("action") == "tool":
                tool_name = decision.get("tool_name")
                arguments = decision.get("arguments", {})

                tool = self.find_tool(tool_name)
                if not tool:
                    return f"The requested tool '{tool_name}' is not available."

                print(f"\nLLM selected tool: {tool_name}")
                print(f"Arguments: {arguments}")

                # Call MCP tool
                result = await self.mcp.call_tool(tool_name, arguments)
                tool_result = self.format_result(result)

                # Generate final natural response
                return await self.generate_final_response(message, tool_result)

            return "I could not understand the assistant's decision."

        except Exception as e:
            print(f"Assistant error: {e}")
            return "Sorry, something went wrong while processing your request."

    # TOOL UTILITIES
    def get_tools_description(self):
        """Return formatted descriptions of available MCP tools."""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"""
                Tool name: {tool['name']}
                Server: {tool['server']}
                Description: {tool['description']}
                Input schema:
                {json.dumps(tool['input_schema'], indent=2)}
                """)
        return "\n".join(descriptions)

    def find_tool(self, tool_name):
        """Find a tool by name."""
        return next((tool for tool in self.tools if tool["name"] == tool_name), None)

    def parse_llm_response(self, response):
        """Parse JSON response from LLM."""
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response)
        except Exception as e:
            print(f"Could not parse LLM response: {e}")
            return {"action": "response", "response": response}

    def format_result(self, result):
        """Format MCP tool result into a readable string."""
        if result is None:
            return "No result returned."
        if hasattr(result, "content"):
            return "\n".join(getattr(item, "text", str(item)) for item in result.content)
        if isinstance(result, dict):
            return json.dumps(result, indent=2)
        return str(result)

    # FINAL RESPONSE GENERATION
    async def generate_final_response(self, user_message, tool_result):
        """Generate a natural response from tool output using LLM."""
        prompt = f"""
            You are an AI personal assistant.

            The user asked:
            {user_message}

            An MCP tool was executed and returned:
            {tool_result}

            Give a short, natural response to the user.
            Do not mention MCP, tools, servers, JSON, or internal implementation details.
            Just explain the result clearly.
            """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2
        )

        return response.choices[0].message.content
