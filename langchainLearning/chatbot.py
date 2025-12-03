from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os

# Load token
load_dotenv()

# Setup model
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    task="text-generation",
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)
model = ChatHuggingFace(llm=llm)

# Chat history memory (in RAM)
chat_history = []

# Prompt template with system + memory + user
chatTemplate = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful customer support agent."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{query}")
])

# Create pipeline
chain = chatTemplate | model

while True:
    userQuery = input("User: ")
    if userQuery.lower() == "exit":
        print("Bye...")
        break

    # Add human message
    chat_history.append(HumanMessage(content=userQuery))

    # Run chain
    result = chain.invoke({"chat_history": chat_history, "query": userQuery})

    # Add AI response to history
    chat_history.append(AIMessage(content=result.content))

    # Print response
    print(f"AI: {result.content}")

print("Final conversation history:", chat_history)
