"""Integration tests for the OxyGent MAS (Multi-Agent System) runtime container.

Tests cover:
- Full lifecycle: init and cleanup via async context manager
- Component registration: duplicate detection, oxy_name_to_oxy population
- Master agent selection: explicit is_master flag, fallback to first agent
- Agent organization tree: hierarchical structure with tools
- Direct invocation via mas.call()
- Chat entry point via mas.chat_with_agent()
- Batch processing via mas.start_batch_processing()
- Agent/tool classification via mas.is_agent()
"""

import pytest

from oxygent.mas import MAS
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyResponse, OxyState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_LLM_OUTPUT = "mock_llm_response"


def _make_mock_llm(name: str = "mock_llm", output: str = MOCK_LLM_OUTPUT) -> MockLLM:
    """Create a MockLLM that returns a fixed string."""

    async def _respond(oxy_request: OxyRequest) -> str:
        return output

    return MockLLM(name=name, func_mock_process=_respond)


def _make_chat_agent(
    name: str = "chat_agent",
    llm_model: str = "mock_llm",
    is_master: bool = False,
    tools: list[str] | None = None,
) -> ChatAgent:
    """Create a ChatAgent with sensible defaults for testing."""
    return ChatAgent(
        name=name,
        llm_model=llm_model,
        prompt="You are a test assistant.",
        is_master=is_master,
        tools=tools or [],
    )


def _make_function_tool(name: str = "test_tool", result: str = "tool_ok") -> FunctionTool:
    """Create a simple FunctionTool that returns a fixed string."""

    async def _func() -> str:
        return result

    return FunctionTool(name=name, desc=f"A test tool: {name}", func_process=_func)


# ============================================================================
# Tests
# ============================================================================


class TestMASLifecycle:
    """Test MAS init/cleanup via the async context manager."""

    @pytest.mark.asyncio
    async def test_mas_lifecycle_init_and_cleanup(self):
        """MAS should register all oxy_space components, initialize the ES client,
        and set the master_agent_name to the ChatAgent after init."""
        mock_llm = _make_mock_llm()
        chat_agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, chat_agent]) as mas:
            # Both components should be registered
            assert "mock_llm" in mas.oxy_name_to_oxy
            assert "chat_agent" in mas.oxy_name_to_oxy
            assert len(mas.oxy_name_to_oxy) == 2

            # ES client should be initialized (MemoryEs via patched config)
            assert mas.es_client is not None

            # The only agent should be selected as master
            assert mas.master_agent_name == "chat_agent"


class TestMASRegistration:
    """Test component registration and duplicate detection."""

    @pytest.mark.asyncio
    async def test_mas_add_oxy_duplicate_raises(self):
        """Adding two oxy components with the same name should raise Exception."""
        mock_llm_1 = _make_mock_llm(name="shared_name")
        mock_llm_2 = _make_mock_llm(name="shared_name")

        with pytest.raises(Exception, match="already exists"):
            async with MAS(oxy_space=[mock_llm_1, mock_llm_2]) as mas:
                pass  # Should not reach here


class TestMasterAgentSelection:
    """Test that init_master_agent_name picks the correct master."""

    @pytest.mark.asyncio
    async def test_mas_master_agent_selection(self):
        """When two agents are registered, the one with is_master=True should
        be selected as the master, even if it is not the first in oxy_space."""
        mock_llm = _make_mock_llm()
        agent_first = _make_chat_agent(name="first_agent", is_master=False)
        agent_master = _make_chat_agent(name="master_agent", is_master=True)

        async with MAS(oxy_space=[mock_llm, agent_first, agent_master]) as mas:
            assert mas.master_agent_name == "master_agent"


class TestAgentOrganization:
    """Test the hierarchical agent organization tree."""

    @pytest.mark.asyncio
    async def test_mas_agent_organization_tree(self):
        """MAS should build a tree with the master agent at the root and its
        permitted tools as children."""
        mock_llm = _make_mock_llm()
        tool_a = _make_function_tool(name="tool_a", result="a_result")
        tool_b = _make_function_tool(name="tool_b", result="b_result")
        master = _make_chat_agent(
            name="master_agent",
            is_master=True,
            tools=["tool_a", "tool_b"],
        )

        async with MAS(oxy_space=[mock_llm, tool_a, tool_b, master]) as mas:
            org = mas.agent_organization

            # Root node should be the master agent
            assert org["name"] == "master_agent"
            assert org["type"] == "agent"

            # Children should include the two tools
            children_names = {child["name"] for child in org.get("children", [])}
            assert "tool_a" in children_names
            assert "tool_b" in children_names


class TestMASCall:
    """Test direct invocation via mas.call()."""

    @pytest.mark.asyncio
    async def test_mas_call_direct_invocation(self):
        """mas.call() should invoke the target oxy and return its output."""
        expected_output = "hello from mock"
        mock_llm = _make_mock_llm(output=expected_output)
        chat_agent = _make_chat_agent()

        async with MAS(oxy_space=[mock_llm, chat_agent]) as mas:
            result = await mas.call(
                callee="chat_agent",
                arguments={"query": "hello"},
            )

            assert result == expected_output


class TestMASChatWithAgent:
    """Test the full chat entry point via mas.chat_with_agent()."""

    @pytest.mark.asyncio
    async def test_mas_chat_with_agent(self):
        """chat_with_agent should route to the master agent and return an
        OxyResponse with COMPLETED state."""
        mock_llm = _make_mock_llm()
        chat_agent = _make_chat_agent(is_master=True)

        async with MAS(oxy_space=[mock_llm, chat_agent]) as mas:
            response = await mas.chat_with_agent(payload={"query": "hello"})

            assert isinstance(response, OxyResponse)
            assert response.state is OxyState.COMPLETED
            assert response.output == MOCK_LLM_OUTPUT


class TestMASBatchProcessing:
    """Test concurrent batch processing."""

    @pytest.mark.asyncio
    async def test_mas_batch_processing(self):
        """start_batch_processing should execute all queries concurrently
        and return one result per query."""
        mock_llm = _make_mock_llm()
        chat_agent = _make_chat_agent(is_master=True)

        async with MAS(oxy_space=[mock_llm, chat_agent]) as mas:
            queries = ["q1", "q2", "q3"]
            results = await mas.start_batch_processing(querys=queries)

            assert len(results) == 3
            for result in results:
                assert result == MOCK_LLM_OUTPUT


class TestMASIsAgent:
    """Test agent vs. tool classification."""

    @pytest.mark.asyncio
    async def test_mas_is_agent_classification(self):
        """is_agent should return True for agents and False for tools."""
        mock_llm = _make_mock_llm()
        chat_agent = _make_chat_agent(name="my_agent")
        tool = _make_function_tool(name="my_tool")

        async with MAS(oxy_space=[mock_llm, chat_agent, tool]) as mas:
            assert mas.is_agent("my_agent") is True
            assert mas.is_agent("my_tool") is False
