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
    return {
        "status": "ok", 
        "message": "Server health is Ok"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)