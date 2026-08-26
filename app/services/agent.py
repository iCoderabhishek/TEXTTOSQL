from app.schemas.chat import ChatRequest
from langchain.agents import create_agent
from app.services.llm import llm
from langchain.tools import tool
from app.schemas.chat import ChatResponse
from app.core.db import get_db
from app.models.user import User
from uuid import UUID
from app.models.sales import Sales

@tool
def generate_sql_query(user_id: UUID, question: str, schema: str, table_name: str) -> ChatResponse:
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

        Here is the table name: {table_name} and here is the schema: \n {schema}. \n Answer this question: {question}
        """
        query= llm.with_structured_output(ChatResponse).invoke(prompt)
        
        return query
    except Exception as e:
        return ChatResponse(response=f"Error...", sql_query=None)




tools = [generate_sql_query]

agent = create_agent(
    model=llm, 
    tools=tools
)

result = agent.invoke({
    "messages": [
        {"role": "system", "content": "The user_id is 123e4567-e89b-12d3-a456-426614174000. The schema is 'CREATE TABLE Sales(amount int);'. The table_name is 'Sales'."},
        {"role": "user", "content": "What is the sales of this month?"}
    ]
})
print(result["messages"][-1].content)