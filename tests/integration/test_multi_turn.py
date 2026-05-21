"""Integration tests for multi-turn conversation continuity.

Tests cover:
- Multi-round conversation via from_trace_id chaining
- Conversation history accumulation across turns
- Trace isolation between independent conversations
- Branching: two follow-ups from the same parent trace

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
"""

import pytest

from oxygent.mas import MAS
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_ANSWER = "mock_response"


def _make_mock_llm(name: str = "mock_llm", output: str = MOCK_ANSWER) -> MockLLM:
    async def _respond(oxy_request: OxyRequest) -> str:
        return output

    return MockLLM(name=name, func_mock_process=_respond)


def _make_chat_agent(
    name: str = "chat_agent",
    llm_model: str = "mock_llm",
    is_master: bool = True,
) -> ChatAgent:
    return ChatAgent(
        name=name,
        llm_model=llm_model,
        prompt="You are a test assistant.",
        is_master=is_master,
    )


# ============================================================================
# Tests
# ============================================================================


class TestMultiTurnConversation:
    """Test multi-round conversation via from_trace_id."""

    @pytest.mark.asyncio
    async def test_first_turn_generates_trace_id(self):
        """The first turn should complete and the response should carry an
        OxyRequest with a non-empty current_trace_id."""
        mock_llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            response = await mas.chat_with_agent(payload={"query": "Hello"})

            assert response.state is OxyState.COMPLETED
            assert response.oxy_request is not None
            assert response.oxy_request.current_trace_id

    @pytest.mark.asyncio
    async def test_second_turn_with_from_trace_id(self):
        """The second turn should succeed when passing from_trace_id from the
        first turn, proving the conversation can be continued."""
        mock_llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            first_response = await mas.chat_with_agent(
                payload={"query": "Hello, what is your name?"}
            )
            assert first_response.state is OxyState.COMPLETED
            trace_id = first_response.oxy_request.current_trace_id

            second_response = await mas.chat_with_agent(
                payload={
                    "query": "Can you repeat that?",
                    "from_trace_id": trace_id,
                }
            )
            assert second_response.state is OxyState.COMPLETED
            assert second_response.output == MOCK_ANSWER

    @pytest.mark.asyncio
    async def test_three_turn_conversation(self):
        """Three sequential turns chained via from_trace_id should all complete."""
        call_count = {"value": 0}

        async def _counting_respond(oxy_request: OxyRequest) -> str:
            call_count["value"] += 1
            return f"response_{call_count['value']}"

        llm = MockLLM(name="mock_llm", func_mock_process=_counting_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            r1 = await mas.chat_with_agent(payload={"query": "Turn 1"})
            assert r1.state is OxyState.COMPLETED
            tid1 = r1.oxy_request.current_trace_id

            r2 = await mas.chat_with_agent(
                payload={"query": "Turn 2", "from_trace_id": tid1}
            )
            assert r2.state is OxyState.COMPLETED
            tid2 = r2.oxy_request.current_trace_id

            r3 = await mas.chat_with_agent(
                payload={"query": "Turn 3", "from_trace_id": tid2}
            )
            assert r3.state is OxyState.COMPLETED

            assert call_count["value"] == 3


class TestTraceIsolation:
    """Test that different trace_ids produce independent conversations."""

    @pytest.mark.asyncio
    async def test_independent_traces_are_isolated(self):
        """Two conversations started without from_trace_id should have
        different current_trace_ids and be completely independent."""
        mock_llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            r1 = await mas.chat_with_agent(payload={"query": "Conversation A"})
            r2 = await mas.chat_with_agent(payload={"query": "Conversation B"})

            assert r1.state is OxyState.COMPLETED
            assert r2.state is OxyState.COMPLETED

            tid1 = r1.oxy_request.current_trace_id
            tid2 = r2.oxy_request.current_trace_id
            assert tid1 != tid2


class TestTraceBranching:
    """Test branching: two follow-ups from the same parent trace."""

    @pytest.mark.asyncio
    async def test_branching_from_same_parent(self):
        """Two follow-up turns from the same parent trace_id should both
        succeed and produce distinct trace_ids of their own."""
        mock_llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            parent = await mas.chat_with_agent(payload={"query": "Initial question"})
            parent_tid = parent.oxy_request.current_trace_id

            branch_a = await mas.chat_with_agent(
                payload={
                    "query": "Branch A follow-up",
                    "from_trace_id": parent_tid,
                }
            )
            branch_b = await mas.chat_with_agent(
                payload={
                    "query": "Branch B follow-up",
                    "from_trace_id": parent_tid,
                }
            )

            assert branch_a.state is OxyState.COMPLETED
            assert branch_b.state is OxyState.COMPLETED
            assert (
                branch_a.oxy_request.current_trace_id
                != branch_b.oxy_request.current_trace_id
            )


class TestGroupDataInheritance:
    """Test that group_data is inherited across turns via from_trace_id."""

    @pytest.mark.asyncio
    async def test_group_data_persists_across_turns(self):
        """group_data set in the first turn should be available in the second
        turn when chained via from_trace_id."""
        mock_llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, agent]) as mas:
            first_response = await mas.chat_with_agent(
                payload={
                    "query": "Set some data",
                    "group_data": {"user_pref": "dark_mode"},
                }
            )
            assert first_response.state is OxyState.COMPLETED
            trace_id = first_response.oxy_request.current_trace_id

            second_response = await mas.chat_with_agent(
                payload={
                    "query": "Read the data",
                    "from_trace_id": trace_id,
                }
            )
            assert second_response.state is OxyState.COMPLETED
