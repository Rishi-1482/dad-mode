from app.services.agent import run_agent


def answer_question(
    question: str,
    include_debug: bool = False,
) -> dict:

    result = run_agent(question)

    if include_debug:
        result["debug_context"] = ""

    return result