import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY is not set in .env"
        )

    return TavilyClient(api_key=api_key)


def search_web(query: str) -> dict:
    response = get_tavily_client().search(
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