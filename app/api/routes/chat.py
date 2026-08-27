from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResumeRequest
from app.services.agent import ask_agent_stream, resume_agent_stream

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        return StreamingResponse(
            ask_agent_stream(user_id=request.user_id, question=request.message),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/resume")
async def chat_resume(request: ChatResumeRequest):
    try:
        return StreamingResponse(
            resume_agent_stream(user_id=request.user_id, decision=request.decision),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))