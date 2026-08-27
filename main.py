from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.chat import router as chat_router
from app.api.routes.user import router as user_router

app = FastAPI(title="SQL Texter AI for Datacruise", description="Chat with your data")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "https://*.0bhishek.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

from app.services.llm import llm
from langchain_core.messages import HumanMessage

@app.get("/")
def health_checking():
    try:
        # Ping the LLM to verify AI health
        llm.invoke([HumanMessage(content="ping")])
        ai_status = "connected"
    except Exception as e:
        ai_status = f"disconnected ({str(e)})"
        
    return {
        "status": "ok", 
        "ai_status": ai_status,
        "message": f"Server health is Ok + AI is {ai_status}"
    }