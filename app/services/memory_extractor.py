import json
import re

from app.services.dad import client
from app.services.memory import save_memory


MEMORY_MODEL = "gpt-4o-mini"


def _extract_json(text: str) -> list[dict]:
    text = text.strip()

    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return json.loads(text)


def extract_memories(
    user_message: str,
    assistant_response: str,
):
    """
    Extract durable, non-sensitive facts that may be useful
    in future conversations.
    """

    instructions = """
You extract long-term memory for an AI assistant.

Only save information that is:
- explicitly stated by the user
- likely to remain useful in future conversations
- non-sensitive

Good examples:
- preferred programming language
- long-term learning goal
- project the user is building
- preferred response style
- recurring professional goal

Do NOT save:
- passwords
- API keys
- financial account information
- medical information
- precise location
- highly sensitive personal information
- temporary or trivial statements

Return ONLY a JSON array.

Example:
[
  {
    "key": "preferred_language",
    "value": "Python",
    "category": "preference"
  }
]

Return [] when there is nothing worth remembering.
"""

    prompt = f"""
USER MESSAGE:
{user_message}

ASSISTANT RESPONSE:
{assistant_response}
"""

    response = client.responses.create(
        model=MEMORY_MODEL,
        instructions=instructions,
        input=prompt,
    )

    try:
        memories = _extract_json(
            response.output_text
        )
    except (json.JSONDecodeError, TypeError):
        return []

    for memory in memories:

        key = memory.get("key")
        value = memory.get("value")
        category = memory.get("category")

        if not key or not value or not category:
            continue

        save_memory(
            memory_key=key,
            memory_value=value,
            category=category,
        )

    return memories