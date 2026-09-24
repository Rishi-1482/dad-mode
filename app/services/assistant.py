import time

from app.services.agent import run_agent
from app.services.observability import log_request


def answer_question(
    question: str,
    conversation_id: str = "default",
    include_debug: bool = False,
) -> dict:

    start = time.perf_counter()

    try:

        result = run_agent(
            question,
            conversation_id=conversation_id,
            include_debug=include_debug,
        )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        log_request(
            conversation_id=conversation_id,
            route=result.get("route", "unknown"),
            tools=result.get("tool_calls", []),
            latency_ms=latency_ms,
            success=result.get("route") != "error",
            model=result.get("model", ""),
        )

        return result

    except Exception:

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        log_request(
            conversation_id=conversation_id,
            route="error",
            tools=[],
            latency_ms=latency_ms,
            success=False,
        )

        raise