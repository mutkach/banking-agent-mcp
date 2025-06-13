## Chat-based interface for a banking application

## Requirements:
1. LangChain stack
2. LangSmith key
3. Cohere for embeddings

### Steps to reproduce:
1. `python mock_sqlite.py`
2. `toolbox --tools-file "tools_sqlite.yaml"`
3. `streamlit run chat_interface.py`
