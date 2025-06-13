import streamlit as st
import bs4
from langchain import hub
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from toolbox_langchain import ToolboxClient
from langchain_cohere import CohereEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
import os

from env import login

st.title("Banking bot")

### INITIALIZE BOT


login()
embeddings = CohereEmbeddings(model="embed-english-v3.0")
loader = UnstructuredMarkdownLoader("rules.md")
vector_store = InMemoryVectorStore(embeddings)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
_ = vector_store.add_documents(documents=all_splits)
retriever = vector_store.as_retriever()

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_terms_of_service",
    "You have access to the terms of services of a banking application. You can resolve user queries and ground them in rules. For example, when asked about interest rates you have to use infromation provided in the rules.",
)

client = ToolboxClient("http://127.0.0.1:5000")
tools = client.load_toolset()
tools.append(retriever_tool)

config = {"configurable": {"thread_id": "thread-1"}}
agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=tools,
    prompt="You are a helpful banking application assistant that may give access to the users' transactions, provide them with helpful material grounded in rules and terms of service documents. You can operate on database within reasonable limits and use external tools to assist customers.",
    checkpointer=MemorySaver()
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def answer_from_bot(prompt:str):
    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]} ,config=config)
    return response['messages'][-1].content

    

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = answer_from_bot(prompt)#f"Echo: {prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})