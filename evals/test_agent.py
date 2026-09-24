import pytest

from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

import app.services.agent as agent_module


CASES = [
    {
        "id": "rag_tool",
        "question": (
            "According to my stored AWS notes, "
            "what is RAG?"
        ),
        "expected_tools": [
            "search_knowledge"
        ],
    },
    {
        "id": "web_tool",
        "question": (
            "What are the latest developments "
            "in generative AI?"
        ),
        "expected_tools": [
            "search_web"
        ],
    },
    {
        "id": "hybrid_tools",
        "question": (
            "Compare my stored AWS notes about RAG "
            "with the latest information on the web."
        ),
        "expected_tools": [
            "search_knowledge",
            "search_web",
        ],
    },
]


def fake_tool(name: str, arguments: dict, user_question: str):

    if name == "search_knowledge":

        return {
            "type": "knowledge",
            "results": [
                {
                    "source": "aws_notes.txt",
                    "document": (
                        "RAG combines information retrieval "
                        "with text generation."
                    ),
                }
            ],
        }

    if name == "search_web":

        return {
            "type": "web",
            "answer": "Current web information.",
            "sources": [
                {
                    "title": "Example source",
                    "url": "https://example.com",
                    "content": "Current information.",
                }
            ],
        }

    raise ValueError(
        f"Unknown tool: {name}"
    )


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=[case["id"] for case in CASES],
)
def test_agent_tools(case, monkeypatch):

    monkeypatch.setattr(
        agent_module,
        "_run_tool",
        fake_tool,
    )

    result = agent_module.run_agent(
        case["question"]
    )

    tools_called = [
        ToolCall(name=name)
        for name in result["tool_calls"]
    ]

    expected_tools = [
        ToolCall(name=name)
        for name in case["expected_tools"]
    ]

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=result["response"],
        tools_called=tools_called,
        expected_tools=expected_tools,
    )

    metric = ToolCorrectnessMetric(
        threshold=0.5,
    )

    assert_test(
        test_case=test_case,
        metrics=[metric],
    )