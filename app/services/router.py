from app.services.dad import client


ROUTER_MODEL = "gpt-4o-mini"


def route_question(question: str) -> str:
    """
    Decide which capability should handle the question.

    Returns:
        normal
        rag
        web
    """

    instructions = """
You are a routing classifier for an AI assistant.

Choose exactly ONE route:

normal
- General knowledge
- Casual conversation
- Questions that do not require the user's documents
- Questions that do not require current web information

rag
- The user is asking about uploaded/private documents
- The user refers to notes, PDFs, files, or the knowledge base
- The answer should come from stored documents

web
- The user asks for current, recent, latest, today's, this week's,
  or otherwise time-sensitive information
- News, current events, current prices, current software versions,
  recent developments, etc.

Return ONLY one word:
normal
rag
or
web
"""

    response = client.responses.create(
        model=ROUTER_MODEL,
        instructions=instructions,
        input=question,
    )

    route = response.output_text.strip().lower()

    if route not in {"normal", "rag", "web"}:
        return "normal"

    return route