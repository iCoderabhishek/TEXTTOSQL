from app.schemas.chat import ChatRequest
from langchain.agents import create_agent
from app.services.llm import llm
from langchain.tools import tool
from sqlalchemy import text, inspect
from app.schemas.chat import ChatResponse, SQLQueryGeneratorRequest
from app.core.db import get_db, engine
from app.models.user import User
from uuid import UUID
from app.models.sales import Sales
from langchain.agents.middleware import ToolErrorMiddleware, ToolRetryMiddleware, ModelFallbackMiddleware, HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from app.services.error import on_error
from langgraph.types import Command



from typing import Optional

@tool(args_schema=SQLQueryGeneratorRequest)
def generate_sql_query(user_id: UUID, question: str, db_schema: Optional[str] = None, table_name: Optional[str] = None) -> ChatResponse:
    """
    Generate SQL query from user's natural language question based on database schema.

    Args:
        question: The natural language question.
        schema: The database schema.
        table_name: The table name.

    Returns:
        A ChatResponse object containing the SQL query.
    """
    db = next(get_db()) 
    valid_user = db.query(User).filter(User.id == user_id).first()

    if( not valid_user or not question):
        return ChatResponse(response="Invalid request", sql_query=None)




    try:

        prompt = f"""
        You are an expert sql query generator, you will generate sql queries based on the database schema and table name provided.
        Generate SQL query from user's natural language question based on database schema.

        Here is the table name: {table_name} and here is the schema: \n {db_schema}. Notice both are optional, user may or may not pass these configs, you should figure out the table name and schema from the question itself. User can say 'find this month sale income' - here both sale and income doesn't exists in db but you should try with similar words until it works like sales, revenue etc. You already have the idea.  \n Answer this question: {question}
        """
        query= llm.with_structured_output(ChatResponse).invoke(prompt)
        
        return query
    except Exception as e:
        print(f"🚨 CRASH REASON: {e}")
        return ChatResponse(response=f"Error...", sql_query=None)




@tool
def execute_sql_query(user_id: UUID, sql_query: str) -> ChatResponse:
    """
    Execute SQL query and return the response.

    Args:
        user_id: The user ID.
        sql_query: The SQL query to execute.

    Returns:
        A ChatResponse object containing the response.
    """
    db = next(get_db()) 
    valid_user = db.query(User).filter(User.id == user_id).first()

    if( not valid_user or not sql_query):
        return ChatResponse(response="Invalid request", sql_query=None)



    try:
        # 1. Wrap raw SQL strings in text() for SQLAlchemy 2.0
        # 2. Fetch the actual rows so the LLM can read the data!
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        
        # Convert the rows to a string so the LLM can read them
        return ChatResponse(response=str(rows), sql_query=sql_query)
    except Exception as e:
        print(f"🚨 CRASH REASON: {e}")
        return ChatResponse(response=f"Error executing query: {e}", sql_query=None)


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
        ModelFallbackMiddleware(
            "amazon.nova-lite-v1:0",
            "meta.llama3-1-8b-instruct-v1:0",
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
    ]
)

db = next(get_db())
test_user = db.query(User).first()
real_user_id = test_user.id if test_user else "123e4567-e89b-12d3-a456-426614174000"




def ask_agent(user_id: UUID, question: str) -> str:
    # 1. Fetch Dynamic Schema
    inspector = inspect(engine)
    schema_text = ""
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_names = [col['name'] for col in columns]
        schema_text += f"Table '{table_name}' has columns: {', '.join(col_names)}.\n"

    # 2. Invoke the Agent
    try:
        result = agent.invoke({
            "messages": [
                {"role": "system", "content": f"The user_id is {user_id}. Here is the exact database schema:\n{schema_text}\n\nIMPORTANT: You are querying PostgreSQL. If a table name has capital letters, you MUST wrap the table name in double quotes in your SQL query (e.g. FROM \"Sales\")."},
                {"role": "user", "content": question}
            ]
        })
        return result["messages"][-1].content
    except Exception as e:
        return f"Agent failed: {str(e)}"



def resume_agent(user_id: UUID, decision: str) -> str:
    config = {"configurable": {"thread_id": user_id}}

    try:

        result = agent.invoke(Command(resume= decision), config)
        return result["messages"][-1].content
    except Exception as e:
        return f"Agent failed to res: {str(e)}"