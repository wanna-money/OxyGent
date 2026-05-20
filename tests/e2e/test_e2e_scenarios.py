"""End-to-end scenario tests for the OxyGent framework.

These tests simulate real user interaction scenarios through the full MAS
pipeline. Every test boots a complete MAS via ``async with MAS(...)`` so
that tool registration, agent initialisation, and the real call mechanism
are exercised --- no monkeypatching of OxyRequest.call.

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory
    make_react_llm_func, make_sequential_llm_func
"""

import json

import pytest

from oxygent.mas import MAS
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.agents.react_agent import ReActAgent
from oxygent.oxy.agents.workflow_agent import WorkflowAgent
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyResponse, OxyState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _static_llm(name: str, output: str) -> MockLLM:
    """Create a MockLLM that always returns *output*."""

    async def _respond(oxy_request: OxyRequest) -> str:
        return output

    return MockLLM(name=name, func_mock_process=_respond)


def _sequential_llm(name: str, responses: list[str]) -> MockLLM:
    """Create a MockLLM that returns *responses* in order, repeating the
    last one once the list is exhausted."""
    idx = {"value": 0}

    async def _respond(oxy_request: OxyRequest) -> str:
        i = idx["value"]
        if i < len(responses):
            result = responses[i]
            idx["value"] += 1
            return result
        return responses[-1]

    return MockLLM(name=name, func_mock_process=_respond)


# ============================================================================
# 1. Single-turn Q&A
# ============================================================================


class TestSingleTurnQA:
    """Verify a simple question-answer through the full MAS pipeline."""

    @pytest.mark.asyncio
    async def test_single_turn_qa(self):
        """MAS with ChatAgent + MockLLM should return a COMPLETED response
        whose output matches the mock answer."""
        expected = "Python is a high-level programming language."
        mock_llm = _static_llm("default_llm", expected)
        agent = ChatAgent(
            name="qa_agent",
            llm_model="default_llm",
            is_master=True,
        )

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            response = await mas.chat_with_agent(
                payload={"query": "What is Python?"}
            )

            assert isinstance(response, OxyResponse)
            assert response.state is OxyState.COMPLETED
            assert response.output == expected


# ============================================================================
# 2. Multi-turn conversation
# ============================================================================


class TestMultiTurnConversation:
    """Verify that sequential queries to the same MAS both complete
    successfully (MAS handles multiple invocations)."""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self):
        """Two sequential chat_with_agent calls should each return a
        COMPLETED OxyResponse."""
        answer_1 = "Python was created by Guido van Rossum."
        answer_2 = "It was first released in 1991."

        mock_llm = _sequential_llm("default_llm", [answer_1, answer_2])
        agent = ChatAgent(
            name="chat_agent",
            llm_model="default_llm",
            is_master=True,
        )

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            response_1 = await mas.chat_with_agent(
                payload={"query": "Who created Python?"}
            )
            assert isinstance(response_1, OxyResponse)
            assert response_1.state is OxyState.COMPLETED
            assert response_1.output == answer_1

            # Second turn, linking to first via from_trace_id
            trace_id_1 = response_1.oxy_request.current_trace_id
            response_2 = await mas.chat_with_agent(
                payload={
                    "query": "When was it released?",
                    "from_trace_id": trace_id_1,
                }
            )
            assert isinstance(response_2, OxyResponse)
            assert response_2.state is OxyState.COMPLETED
            assert response_2.output == answer_2


# ============================================================================
# 3. ReAct tool-use scenario
# ============================================================================


class TestReActToolUse:
    """ReActAgent calls a calculator tool and synthesises the result."""

    @pytest.mark.asyncio
    async def test_react_tool_use_scenario(self):
        """The agent should invoke the calculator, observe the result, and
        return a final answer that incorporates the calculation."""
        tool_call_json = json.dumps(
            {"tool_name": "calculator", "arguments": {"expression": "2+3"}}
        )
        final_answer = "The answer is 5."

        # The LLM returns a tool-call on the first round, then the final
        # answer once it sees the observation.
        call_idx = {"value": 0}

        async def _react_llm(oxy_request: OxyRequest) -> str:
            messages = oxy_request.arguments.get("messages", [])
            has_observation = any(
                "execution result" in str(m.get("content", "")).lower()
                for m in messages
                if isinstance(m, dict)
            )
            if call_idx["value"] == 0 and not has_observation:
                call_idx["value"] += 1
                return tool_call_json
            return final_answer

        mock_llm = MockLLM(name="default_llm", func_mock_process=_react_llm)

        async def calc(expression: str = "0") -> str:
            return str(eval(expression))  # noqa: S307

        calculator = FunctionTool(
            name="calculator",
            desc="Evaluates a mathematical expression.",
            func_process=calc,
        )

        agent = ReActAgent(
            name="react_agent",
            llm_model="default_llm",
            tools=["calculator"],
            is_master=True,
            trust_mode=True,
            max_react_rounds=5,
        )

        async with MAS(oxy_space=[mock_llm, calculator, agent]) as mas:
            response = await mas.chat_with_agent(
                payload={"query": "What is 2 + 3?"}
            )

            assert isinstance(response, OxyResponse)
            assert response.state is OxyState.COMPLETED
            # trust_mode returns the tool observation directly
            assert "5" in response.output


# ============================================================================
# 4. Multi-agent delegation
# ============================================================================


class TestMultiAgentDelegation:
    """Master ReActAgent delegates to a sub-agent ChatAgent and synthesises
    the result."""

    @pytest.mark.asyncio
    async def test_multi_agent_delegation(self):
        """The master agent should delegate to the expert, receive its
        answer, and return a final response."""

        # The expert's LLM always produces a domain-specific answer.
        expert_llm = _static_llm(
            "expert_llm",
            "Photosynthesis converts sunlight into chemical energy.",
        )

        expert_agent = ChatAgent(
            name="expert_agent",
            llm_model="expert_llm",
        )

        # The master LLM: first call emits a delegation tool-call; after
        # observing the expert's answer it produces the final response.
        delegation_json = json.dumps(
            {
                "tool_name": "expert_agent",
                "arguments": {"query": "Explain photosynthesis."},
            }
        )
        final_answer = (
            "According to the expert, photosynthesis converts sunlight "
            "into chemical energy."
        )

        call_idx = {"value": 0}

        async def _master_llm(oxy_request: OxyRequest) -> str:
            messages = oxy_request.arguments.get("messages", [])
            has_observation = any(
                "execution result" in str(m.get("content", "")).lower()
                for m in messages
                if isinstance(m, dict)
            )
            if call_idx["value"] == 0 and not has_observation:
                call_idx["value"] += 1
                return delegation_json
            return final_answer

        master_llm = MockLLM(name="master_llm", func_mock_process=_master_llm)

        master_agent = ReActAgent(
            name="master_agent",
            llm_model="master_llm",
            sub_agents=["expert_agent"],
            is_master=True,
            max_react_rounds=5,
        )

        async with MAS(
            oxy_space=[expert_llm, expert_agent, master_llm, master_agent]
        ) as mas:
            response = await mas.chat_with_agent(
                payload={"query": "Tell me about photosynthesis."}
            )

            assert isinstance(response, OxyResponse)
            assert response.state is OxyState.COMPLETED
            assert "photosynthesis" in response.output.lower()


# ============================================================================
# 5. Error recovery on tool failure
# ============================================================================


class TestErrorRecoveryOnToolFailure:
    """When a tool raises an exception the ReActAgent should handle it
    gracefully (no crash) and still produce output."""

    @pytest.mark.asyncio
    async def test_error_recovery_on_tool_failure(self):
        """A tool that raises should not crash the agent; the agent should
        recover and return some output."""
        tool_call_json = json.dumps(
            {"tool_name": "flaky_tool", "arguments": {"input": "test"}}
        )
        fallback_answer = "I could not complete the tool call, but here is my best answer."

        call_idx = {"value": 0}

        async def _llm_func(oxy_request: OxyRequest) -> str:
            messages = oxy_request.arguments.get("messages", [])
            has_observation = any(
                "execution result" in str(m.get("content", "")).lower()
                for m in messages
                if isinstance(m, dict)
            )
            if call_idx["value"] == 0 and not has_observation:
                call_idx["value"] += 1
                return tool_call_json
            return fallback_answer

        mock_llm = MockLLM(name="default_llm", func_mock_process=_llm_func)

        async def flaky_func(input: str = "") -> str:
            raise RuntimeError("Simulated tool failure")

        flaky_tool = FunctionTool(
            name="flaky_tool",
            desc="A tool that always fails.",
            func_process=flaky_func,
        )

        agent = ReActAgent(
            name="react_agent",
            llm_model="default_llm",
            tools=["flaky_tool"],
            is_master=True,
            max_react_rounds=5,
        )

        async with MAS(oxy_space=[mock_llm, flaky_tool, agent]) as mas:
            response = await mas.chat_with_agent(
                payload={"query": "Use the tool please."}
            )

            assert isinstance(response, OxyResponse)
            assert response.state is OxyState.COMPLETED
            # The agent should have produced *some* output rather than crashing
            assert len(response.output) > 0


# ============================================================================
# 6. WorkflowAgent end-to-end
# ============================================================================


class TestWorkflowEndToEnd:
    """WorkflowAgent executes a user-defined async function through the
    full MAS lifecycle."""

    @pytest.mark.asyncio
    async def test_workflow_end_to_end(self):
        """The workflow function should receive the query, process it, and
        return the result via the MAS pipeline."""
        mock_llm = _static_llm("default_llm", "unused")

        async def my_workflow(oxy_request: OxyRequest) -> str:
            query = oxy_request.get_query()
            return f"Workflow processed: {query}"

        workflow_agent = WorkflowAgent(
            name="workflow_agent",
            llm_model="default_llm",
            func_workflow=my_workflow,
            is_master=True,
        )

        async with MAS(oxy_space=[mock_llm, workflow_agent]) as mas:
            response = await mas.chat_with_agent(
                payload={"query": "Run my pipeline"}
            )

            assert isinstance(response, OxyResponse)
            assert response.state is OxyState.COMPLETED
            assert response.output == "Workflow processed: Run my pipeline"
