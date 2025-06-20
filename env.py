import os
import getpass

def login():
    os.environ["COHERE_API_KEY"] = getpass.getpass("Enter API key for Cohere: ")
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter API key for LangSmith: ")
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGSMITH_PROJECT"] = "pr-drab-canvas-1"
    os.environ["ANTHROPIC_API_KEY"] = getpass.getpass("Enter API key for Anthropic: ")
