import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set in .env")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)


def search_web(query: str) -> dict:
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True,
    )

    sources = []

    for result in response.get("results", []):
        sources.append(
            {
                "title": result.get("title", "Untitled"),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0),
            }
        )

    return {
        "answer": response.get("answer"),
        "sources": sources,
    }