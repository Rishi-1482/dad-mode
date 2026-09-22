# Dad Mode AI Assistant

An AI assistant that answers text and voice questions with practical advice, RAG-powered knowledge, web search, and just enough disappointed-dad energy.

## Live app

[Open Dad Mode](https://rishi-1482-dad-mode-frontendstreamlit-app-mdotaw.streamlit.app/)

Go ahead. Ask the question you could have Googled yourself.

## Features

- Text and voice conversations
- Speech-to-text and text-to-speech
- RAG with ChromaDB
- Web search with Tavily
- FastAPI backend and Streamlit frontend
- Input guardrails and API token protection

## Local setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key
APP_API_TOKEN=your-private-token
```

Run the backend:

```bash
uvicorn app.api.main:app --reload
```

Run the frontend:

```bash
streamlit run frontend/streamlit_app.py
```

That is it. Even Dad thinks you can handle this part.
