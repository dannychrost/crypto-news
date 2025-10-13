from langchain_core.tools import tool
# from langchain_community.llms import Ollama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
import requests
@tool
def get_health():
    """
    Retrieve the server health status.

    Sends a GET request to the health endpoint and returns a JSON object containing information about the server status.

    Returns:
        dict: A dictionary with the following keys:
            - "status" (str): The status of the server.
            - "timestamp" (str): The timestamp of the server status.
            - "database" (str): The status of the database connection.
    """
    response = requests.get("http://localhost:8000/health")
    return response.json()

@tool
def get_db_news(start_date: str, end_date: str):
    """
    Fetch the latest cryptocurrency news from the database via a GET request to the news endpoint.

    Parameters:
        start_date (str): The start date for filtering news items in ISO8601 format (e.g., "2025-09-01T00:00:00+00:00").
        end_date (str): The end date for filtering news items in ISO8601 format (e.g., "2025-09-30T23:59:59+00:00").

    Returns:
        dict: A dictionary with the following keys:
            - "success" (bool): Indicates whether the request was successful.
            - "message" (str): A message describing the result.
            - "items_retrieved" (int): The number of news items retrieved.
            - "data" (list): A list of news article dictionaries. Each article contains:
                - "id" (int): The unique identifier of the news article.
                - "slug" (str): A URL-friendly string representing the article.
                - "title" (str): The title of the news article.
                - "description" (str): A summary or description of the news article.
                - "published_at" (str): The publication timestamp in ISO8601 format.
                - "created_at" (str): The creation timestamp in ISO8601 format.
                - "kind" (str): The category or type of news.
    """
    response = requests.get("http://localhost:8000/api/v1/news", params={"start": start_date, "end": end_date})
    return response.json()
     

# Load Llama 3.1 via Ollama
llm = ChatOllama(model="llama3.1:8b")
system_prompt = """
You are a crypto news assistant named Atlas.
- Your goal is to provide accurate, concise, and helpful answers about crypto news and related events.
- You have access to several tools (database queries, health checks).

Tool usage rules:
- Use tools **only when necessary** to answer user questions about crypto news (e.g. "What happened with ETH this week?").
- If the question is general or unrelated to crypto, respond directly without calling tools.
- The get_health tool can be used to check the health of the server and to also get the current timestamp.
- Do NOT mention tool names, tool usage, or your internal reasoning to the user.
- If the database returns no results, say exactly: "No news found for that time period." Do not fabricate news or speculate.

Answering style:
- Summarize retrieved news clearly and factually.
- For general conceptual questions, answer plainly without jargon.
- Keep answers concise, professional, and focused on the user’s intent.
- Do NOT tell the user to rephrase or be more specific.
- Do NOT explain whether a tool was used or not.
- Only output the final, user-facing answer.
"""

# Basic memory storage with conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{chat_history}"),  
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create a tool-calling agent by passing the LLM directly without binding tools explicitly
agent = create_tool_calling_agent(llm, [get_db_news, get_health], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[get_db_news, get_health], memory=memory, verbose=True)

# Loop the agent executor, having the user input their message, and the agent executor will return the response
while True:
    user_input = input("User: ")
    result = agent_executor.invoke({"input": user_input})
    print(result["output"])