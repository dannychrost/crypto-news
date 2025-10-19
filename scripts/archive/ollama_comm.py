from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory
from app.tools import get_health, get_db_news
from app.prompts import system_prompt

# Load Llama 3.1 via Ollama
llm = ChatOllama(model="llama3.1:8b")

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