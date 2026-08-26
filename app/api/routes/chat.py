from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import ask_agent


router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer_string = ask_agent(user_id=request.user_id, question=request.message)
        
        return ChatResponse(
            response=answer_string, 
            sql_query=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))