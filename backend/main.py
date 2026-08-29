from contextlib import asynccontextmanager
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from assistant import Assistant

assistant = Assistant()

@asynccontextmanager #  unified way to manage resources that need both setup and teardown in an asynchronous environment.
async def lifespan(app: FastAPI):
    print("Starting AI Personal Assistant...")
    try:
        await assistant.initialize()
        print("AI Personal Assistant started successfully.")
        yield

    finally: # when i click "CTRL + C" to stop the backend
        print("Shutting down AI Personal Assistant...")
        await assistant.shutdown()
        print("AI Personal Assistant stopped.")


app = FastAPI(
    title="AI Personal Assistant",
    description="AI Personal Assistant using MCP",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Pydantic models 
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str

# Health check for root api
@app.get("/")
async def root():
    return {
        "message": "AI Personal Assistant is running",
        "status": "online",
        "mcp": "enabled"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        return ChatResponse(response="Please enter a message.")

    try:
        result = await assistant.process(message)
        return ChatResponse(response=result)
    except Exception as e:
        print(f"Chat error: {e}")
        return ChatResponse(response="Sorry, I couldn't process your request.")
