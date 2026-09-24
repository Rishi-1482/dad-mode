from app.services.agent import run_agent


def answer_question(
    question: str,
    include_debug: bool = False,
) -> dict:
    return run_agent(
        question,
        include_debug=include_debug,
    )