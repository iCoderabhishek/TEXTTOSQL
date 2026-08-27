from app.schemas.chat import ChatRequest
from langchain.agents import create_agent
from app.services.llm import llm
from langchain.tools import tool
from sqlalchemy import text, inspect
from app.schemas.chat import ChatResponse, SQLQueryGeneratorRequest
from app.core.db import SessionLocal, engine
from app.models.user import User
from uuid import UUID
from app.models.sales import Sales
from langchain.agents.middleware import ToolErrorMiddleware, ToolRetryMiddleware, ModelFallbackMiddleware, HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from app.services.error import on_error
from langgraph.types import Command



from typing import Optional

@tool(args_schema=SQLQueryGeneratorRequest)
def generate_sql_query(user_id: UUID, question: str, db_schema: Optional[str] = None, table_name: Optional[str] = None) -> str:
    """
    Generate SQL query from user's natural language question based on database schema.

    Args:
        question: The natural language question.
        schema: The database schema.
        table_name: The table name.

    Returns:
        A string containing the SQL query response in JSON format.
    """
    db = SessionLocal()
    try:
        valid_user = db.query(User).filter(User.id == user_id).first()
        if not valid_user or not question:
            return f"Error: User {user_id} not found or question is empty."
    finally:
        db.close()




    try:

        prompt = f"""
        You are an expert sql query generator, you will generate sql queries based on the database schema and table name provided.
        Generate SQL query from user's natural language question based on database schema.

        Here is the table name: {table_name} and here is the schema: \n {db_schema}. Notice both are optional, user may or may not pass these configs, you should figure out the table name and schema from the question itself. User can say 'find this month sale income' - here both sale and income doesn't exists in db but you should try with similar words until it works like sales, revenue etc. You already have the idea.  \n Answer this question: {question}
        """
        query= llm.with_structured_output(ChatResponse).invoke(prompt)
        
        return query.model_dump_json()
    except Exception as e:
        print(f"🚨 CRASH REASON: {e}")
        return f"Error: {e}"




@tool
def execute_sql_query(user_id: UUID, sql_query: str) -> str:
    """
    Execute SQL query and return the response.

    Args:
        user_id: The user ID.
        sql_query: The SQL query to execute.

    Returns:
        A string containing the results of the executed query.
    """
    db = SessionLocal()
    try:
        valid_user = db.query(User).filter(User.id == user_id).first()
        if not valid_user or not sql_query:
            return f"Error: User {user_id} not found or query is empty."
        
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        
        # Convert the rows to a string so the LLM can read them
        return str(rows)
    except Exception as e:
        print(f"🚨 CRASH REASON: {e}")
        return f"Error executing query: {e}"
    finally:
        db.close()


# create and test tools here ####

tools = [generate_sql_query, execute_sql_query]


agent = create_agent(
    model=llm, 
    tools=tools,
    middleware=[
        ToolErrorMiddleware(on_error),  
        ToolRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ), 

        HumanInTheLoopMiddleware(
            interrupt_on={
                "execute_sql_query":{
                    "allowed_decisions": [
                        "approve", "edit", "reject"
                    ]
                }
            }
        )
    ],
    checkpointer=InMemorySaver()
)






import json
from langchain_core.messages import AIMessageChunk

async def ask_agent_stream(user_id: UUID, question: str):
    # 1. Fetch Dynamic Schema
    inspector = inspect(engine)
    schema_text = ""
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_names = [col['name'] for col in columns]
        schema_text += f"Table '{table_name}' has columns: {', '.join(col_names)}.\n"

    # 2. Invoke the Agent
    config = {"configurable": {"thread_id": str(user_id)}}
    inputs = {
        "messages": [
            {"role": "system", "content": f"The user_id is {user_id}. Here is the exact database schema:\n{schema_text}\n\nIMPORTANT: You are querying PostgreSQL. If a table name has capital letters, you MUST wrap the table name in double quotes in your SQL query (e.g. FROM \"Sales\")."},
            {"role": "user", "content": question}
        ]
    }
    
    try:
        async for chunk in agent.astream(inputs, config, stream_mode="messages"):
            msg, metadata = chunk
            
            if isinstance(msg, AIMessageChunk):
                if msg.content:
                    text_content = ""
                    if isinstance(msg.content, list):
                        for block in msg.content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_content += block.get("text", "")
                    elif isinstance(msg.content, str):
                        text_content = msg.content
                        
                    if text_content:
                        yield f"data: {json.dumps({'type': 'content', 'content': text_content})}\n\n"

                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        if tc.get("name") == "execute_sql_query":
                            sql_query = tc.get("args", {}).get("sql_query", "")
                            yield f"data: {json.dumps({'type': 'tool_call', 'sql_query': sql_query})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


async def resume_agent_stream(user_id: UUID, decision: str):
    config = {"configurable": {"thread_id": str(user_id)}}
    
    # HumanInTheLoopMiddleware expects a dictionary with "decisions" list
    hitl_decision = {
        "decisions": [
            {
                "type": decision
            }
        ]
    }

    try:
        async for chunk in agent.astream(Command(resume=hitl_decision), config, stream_mode="messages"):
            msg, metadata = chunk
            
            if isinstance(msg, AIMessageChunk):
                if msg.content:
                    text_content = ""
                    if isinstance(msg.content, list):
                        for block in msg.content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_content += block.get("text", "")
                    elif isinstance(msg.content, str):
                        text_content = msg.content
                        
                    if text_content:
                        yield f"data: {json.dumps({'type': 'content', 'content': text_content})}\n\n"

                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        if tc.get("name") == "execute_sql_query":
                            sql_query = tc.get("args", {}).get("sql_query", "")
                            yield f"data: {json.dumps({'type': 'tool_call', 'sql_query': sql_query})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"