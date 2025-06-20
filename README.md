## Chat-based interface for a banking application

## Requirements:
0. Anthropic key
1. LangSmith key
2. LangChain stack
3. Cohere for embeddings

### Steps to reproduce:
1. `python mock_sqlite.py` -- to fill DB with mock data
2. `toolbox --tools-file "tools_sqlite.yaml"` 
3. `streamlit run chat_interface.py`
