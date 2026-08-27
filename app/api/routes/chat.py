from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, ChatResumeRequest
from app.services.agent import ask_agent, resume_agent


router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer_content = ask_agent(user_id=request.user_id, question=request.message)
        
        sql_query = None
        response_text = answer_content
        
        # If the LLM returned a tool call for execute_sql_query (list format)
        if isinstance(answer_content, list):
            for block in answer_content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    if block.get("name") == "execute_sql_query":
                        sql_query = block.get("input", {}).get("sql_query")
                        response_text = "I generated the following SQL query. Would you like to execute it?"
                        break
            
            # If we didn't find an execute_sql_query tool call, extract the normal text
            if sql_query is None:
                text_blocks = [
                    block.get("text", "") 
                    for block in answer_content 
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if text_blocks:
                    response_text = "".join(text_blocks)
        
        return ChatResponse(
            response=response_text, 
            sql_query=sql_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/chat/resume", response_model=ChatResponse)
def chat_resume(request: ChatResumeRequest):
    try:
        answer_content = resume_agent(user_id=request.user_id, decision=request.decision)
        
        sql_query = None
        response_text = answer_content
        
        # If the LLM returned another tool call
        if isinstance(answer_content, list):
            for block in answer_content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    if block.get("name") == "execute_sql_query":
                        sql_query = block.get("input", {}).get("sql_query")
                        response_text = "I generated the following SQL query. Would you like to execute it?"
                        break
            
            # If we didn't find an execute_sql_query tool call, extract the normal text
            if sql_query is None:
                text_blocks = [
                    block.get("text", "") 
                    for block in answer_content 
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if text_blocks:
                    response_text = "".join(text_blocks)
        
        return ChatResponse(
            response=response_text, 
            sql_query=sql_query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))