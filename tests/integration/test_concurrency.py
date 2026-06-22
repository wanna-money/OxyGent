"""Integration tests for batch processing and concurrent execution.

Tests cover:
- mas.start_batch_processing() with multiple payloads
- Verify all payloads get responses
- start_batch_processing with return_trace_id=True
- Concurrent chat_with_agent requests maintain isolation

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
"""

import asyncio

import pytest

from oxygent.mas import MAS
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_llm(name: str = "mock_llm") -> MockLLM:
    async def _respond(oxy_request: OxyRequest) -> str:
        query = oxy_request.get_query()
        return f"answer_for:{query}"

    return MockLLM(name=name, func_mock_process=_respond)


def _make_chat_agent(
    name: str = "chat_agent",
    is_master: bool = True,
) -> ChatAgent:
    return ChatAgent(
        name=name,
        llm_model="mock_llm",
        prompt="You are a test assistant.",
        is_master=is_master,
    )


# ============================================================================
# Tests
# ============================================================================


class TestBatchProcessing:
    """Test start_batch_processing() with multiple queries."""

    @pytest.mark.asyncio
    async def test_batch_processes_all_queries(self):
        """start_batch_processing should return one result per query."""
        llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            queries = ["query_1", "query_2", "query_3", "query_4"]
            results = await mas.start_batch_processing(querys=queries)

            assert len(results) == 4
            for result in results:
                assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_batch_single_query(self):
        """start_batch_processing with a single query should still work."""
        llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            results = await mas.start_batch_processing(querys=["only_one"])

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_batch_with_return_trace_id(self):
        """start_batch_processing with return_trace_id=True should return
        dicts containing output and trace_id."""
        llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            queries = ["q1", "q2"]
            results = await mas.start_batch_processing(
                querys=queries, return_trace_id=True
            )

            assert len(results) == 2
            for result in results:
                assert isinstance(result, dict)
                assert "output" in result
                assert "trace_id" in result
                assert result["trace_id"]  # non-empty


class TestConcurrentChatIsolation:
    """Test that concurrent chat_with_agent calls maintain isolation."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_produce_independent_results(self):
        """Multiple asyncio.gather'd chat_with_agent calls should each
        produce independent, correct results."""
        call_log = []

        async def _respond(oxy_request: OxyRequest) -> str:
            query = oxy_request.get_query()
            call_log.append(query)
            await asyncio.sleep(0.01)
            return f"response_for:{query}"

        llm = MockLLM(name="mock_llm", func_mock_process=_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            tasks = [
                mas.chat_with_agent(payload={"query": f"concurrent_{i}"})
                for i in range(5)
            ]
            responses = await asyncio.gather(*tasks)

            assert len(responses) == 5
            for resp in responses:
                assert resp.state is OxyState.COMPLETED

            assert len(call_log) == 5

    @pytest.mark.asyncio
    async def test_concurrent_requests_have_unique_trace_ids(self):
        """Concurrent requests should each get a unique trace_id."""
        llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            tasks = [
                mas.chat_with_agent(payload={"query": f"trace_test_{i}"})
                for i in range(3)
            ]
            responses = await asyncio.gather(*tasks)

            trace_ids = {r.oxy_request.current_trace_id for r in responses}
            assert len(trace_ids) == 3, (
                "Each concurrent request should have a unique trace_id"
            )


class TestBatchEmpty:
    """Test edge case: batch with empty query list."""

    @pytest.mark.asyncio
    async def test_batch_empty_query_list(self):
        """start_batch_processing with an empty list should return empty."""
        llm = _make_mock_llm()
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            results = await mas.start_batch_processing(querys=[])
            assert results == []
