import re

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=API_KEY)


MAX_INPUT_LENGTH = 4000


# Basic prompt-injection patterns.
# These are not a complete security solution, but they are
# useful as a first defensive layer for our prototype.
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all|any|the|your) previous instructions",
    r"ignore (all|any|the) instructions above",
    r"forget (all|any|the) previous instructions",
    r"disregard (all|any|the) previous instructions",
    r"reveal (your|the) system prompt",
    r"show (me )?(your|the) system prompt",
    r"reveal (your|the) developer message",
    r"reveal (your|the) api key",
    r"reveal (your|the) secret",
    r"print (your|the) system prompt",
    r"you are now (a|an)",
]


def detect_prompt_injection(text: str) -> bool:
    """
    Detect common prompt-injection patterns.
    """

    normalized = text.lower().strip()

    return any(
        re.search(pattern, normalized)
        for pattern in PROMPT_INJECTION_PATTERNS
    )


def moderate_text(text: str) -> dict:
    """
    Run OpenAI moderation on user text.
    """

    moderation = client.moderations.create(
        model="omni-moderation-latest",
        input=text,
    )

    result = moderation.results[0]

    return {
        "flagged": result.flagged,
        "categories": result.categories,
    }


def validate_input(text: str) -> dict:
    """
    Run all input guardrails.
    """

    if not text or not text.strip():
        return {
            "allowed": False,
            "reason": "empty_input",
        }

    if len(text) > MAX_INPUT_LENGTH:
        return {
            "allowed": False,
            "reason": "input_too_long",
        }

    if detect_prompt_injection(text):
        return {
            "allowed": False,
            "reason": "prompt_injection",
        }

    moderation = moderate_text(text)

    if moderation["flagged"]:
        return {
            "allowed": False,
            "reason": "content_policy",
            "categories": moderation["categories"],
        }

    return {
        "allowed": True,
        "reason": None,
    }


def validate_output(text: str) -> dict:
    """
    Moderate the generated response before returning it.
    """

    moderation = moderate_text(text)

    if moderation["flagged"]:
        return {
            "allowed": False,
            "reason": "output_policy",
            "categories": moderation["categories"],
        }

    return {
        "allowed": True,
        "reason": None,
    }