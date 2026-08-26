from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from app.core.config import settings

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
)


@tool
def get_weather(city: str) -> str:
    """Get the weather of a city"""
    return f"The weather of {city} is rainy & 21 deg Celcius"


llm_with_tools = llm.bind_tools(
    tools=[get_weather],
    tool_config={
        "function_calling_config": {
            "mode": "AUTO",  # Modes: ANY (force tool), AUTO (let LLM decide), NONE (disable)
        }
    }
)


messages = [{"role": "user", "content": "Hi, this is Abhishek, I am calling you from my app. what is the weather in Jalpaiguri?"}]
ai_msg = llm_with_tools.invoke(messages)
messages.append(ai_msg)

print(f"LLM wants to call: {ai_msg.tool_calls}")


from langchain_core.messages import ToolMessage

for tool_call in ai_msg.tool_calls:
    tool_result = get_weather.invoke(tool_call)
    # The LLM NEEDS to know WHICH tool call this result belongs to!
    messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"]))

final_response = llm_with_tools.invoke(messages)

print(final_response.content)

# response = llm.invoke("Hi, this is Abhishek, I am calling you from my app.")
