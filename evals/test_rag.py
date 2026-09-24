# test to check if the agent is calling the right tools
import json
from pathlib import Path

import pytest

from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app.services.assistant import answer_question


DATASET_PATH = Path("/Users/rishienugala/Desktop/local-agent-AI-voice-assistant/app/evaluation/dataset.json")


def load_rag_cases():
    data = json.loads(
        DATASET_PATH.read_text(encoding="utf-8")
    )

    return [
        case
        for case in data
        if case["expected_route"] == "rag"
    ]


RAG_CASES = load_rag_cases()


@pytest.mark.parametrize(
    "case",
    RAG_CASES,
    ids=[case["id"] for case in RAG_CASES],
)
def test_rag(case):

    result = answer_question(
        case["question"],
        include_debug=True,
    )

    context = result.get(
        "debug_context",
        "",
    )

    retrieval_context = [
        chunk.strip()
        for chunk in context.split("\n\n---\n\n")
        if chunk.strip()
    ]

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=result["response"],
        expected_output=case.get(
            "reference_answer"
        ),
        retrieval_context=retrieval_context,
    )

    metrics = [
        AnswerRelevancyMetric(
            threshold=0.5,
            model="gpt-4o-mini",
        ),
        FaithfulnessMetric(
            threshold=0.5,
            model="gpt-4o-mini",
        ),
        ContextualRelevancyMetric(
            threshold=0.5,
            model="gpt-4o-mini",
        ),
    ]

    assert result["route"] == "rag"

    assert_test(
        test_case=test_case,
        metrics=metrics,
    )