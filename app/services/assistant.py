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
            input_tokens=result.get("input_tokens", 0),
            output_tokens=result.get("output_tokens", 0),
            estimated_cost=result.get("estimated_cost", 0.0),
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
            model="",
        )

        raise