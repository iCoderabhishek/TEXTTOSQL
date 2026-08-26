from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import ask_agent


router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = ask_agent(user_id=request.user_id, question=request.question)
        print(result)
        return ChatResponse(response=result.content if result.content else "Error", sql_query=result.sql_query if result.sql_query else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        detail = str(e)