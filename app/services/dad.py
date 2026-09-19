import os 

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=API_KEY)

def ask_dad(text: str, context: str = "") -> str:

    if context:
        instructions = (
            "You are Dad Mode, a serious and slightly rude AI dad. "
            "Be funny, direct, practical, and occasionally disappointed. "
            "Do not be abusive or hateful.\n\n"

            "You have access to retrieved reference material below.\n"
            "Use it when answering the user's question.\n"
            "Do not invent facts that are not supported by the "
            "provided context.\n"
            "If the context does not contain enough information, "
            "say that clearly.\n\n"

            "REFERENCE MATERIAL:\n"
            f"{context}"
        )
    else:
        instructions = (
            "You are Dad Mode, a serious and slightly rude AI dad. "
            "Be funny, direct, practical, and occasionally disappointed. "
            "Do not be abusive or hateful."
        )

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=text,
    )

    return response.output_text