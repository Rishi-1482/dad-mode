from app.services.dad import ask_dad
from app.services.rag import retrieve
from app.services.router import route_question
from app.services.web import search_web
from app.services.guardrails import validate_input


def answer_question(question: str) -> dict:
    """
    Route the question to the appropriate AI capability.
    """

    safety = validate_input(question)

    if not safety["allowed"]:
        return {
            "response": (
                "Dad isn't answering that one. "
                "Try asking something useful."
            ),
            "route": "blocked",
            "sources": [],
            "safety": safety,
        }

    route = route_question(question)

    # -------------------------
    # Normal LLM
    # -------------------------

    if route == "normal":

        response = ask_dad(question)

        return {
            "response": response,
            "route": "normal",
            "sources": [],
        }

    # -------------------------
    # RAG
    # -------------------------

    if route == "rag":

        results = retrieve(
            question,
            n_results=3,
        )

        if not results:

            response = ask_dad(
                question,
                context=(
                    "No relevant documents were found in "
                    "the knowledge base."
                ),
            )

            return {
                "response": response,
                "route": "rag",
                "sources": [],
            }

        context_parts = []

        for result in results:

            context_parts.append(
                f"Source: {result['source']}\n"
                f"{result['document']}"
            )

        context = "\n\n---\n\n".join(context_parts)

        response = ask_dad(
            question,
            context=context,
        )

        sources = list(
            dict.fromkeys(
                result["source"]
                for result in results
            )
        )

        return {
            "response": response,
            "route": "rag",
            "sources": sources,
        }

    # -------------------------
    # Web Search
    # -------------------------

    if route == "web":

        result = search_web(question)

        # Build context from search results.
        context_parts = []

        for source in result["sources"]:

            content = source.get("content", "")

            # Keep context reasonably small.
            content = content[:3000]

            context_parts.append(
                f"Source: {source['title']}\n"
                f"URL: {source['url']}\n"
                f"{content}"
            )

        context = "\n\n---\n\n".join(context_parts)

        response = ask_dad(
            question,
            context=context,
        )

        return {
            "response": response,
            "route": "web",
            "sources": result["sources"],
        }

    # -------------------------
    # Safety fallback
    # -------------------------

    response = ask_dad(question)

    return {
        "response": response,
        "route": "normal",
        "sources": [],
    }