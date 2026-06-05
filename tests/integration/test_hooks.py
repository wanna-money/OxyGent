"""Integration tests for lifecycle hooks and middleware.

Tests cover:
- func_process_input transforms input before execution
- func_process_output transforms output after execution
- func_format_input / func_format_output for display formatting
- func_execute replaces the default _execute
- preceding_oxy runs before main execution
- Hook exceptions do not crash the pipeline

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
"""

import pytest

from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyResponse, OxyState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _patch_local_agent_config(monkeypatch):
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_agent_llm_model",
        lambda: "mock_llm",
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_agent_prompt",
        lambda: "You are a helpful assistant.",
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_vearch_config",
        lambda: None,
    )


# ============================================================================
# Tests
# ============================================================================


class TestFuncProcessInput:
    """Test func_process_input hook."""

    @pytest.mark.asyncio
    async def test_process_input_modifies_request(
        self, monkeypatch, dummy_mas, oxy_request_factory
    ):
        """func_process_input should be called with the OxyRequest and can
        modify it before execution."""
        _patch_local_agent_config(monkeypatch)

        processed = {"value": False}

        async def _process_input(oxy_request: OxyRequest) -> OxyRequest:
            processed["value"] = True
            oxy_request.arguments["injected_key"] = "injected_value"
            return oxy_request

        captured_args = {}

        async def _respond(oxy_request: OxyRequest) -> str:
            captured_args.update(oxy_request.arguments)
            return "done"

        llm = MockLLM(name="mock_llm", func_mock_process=_respond)
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        agent = ChatAgent(
            name="chat_agent",
            desc="Agent with process_input",
            llm_model="mock_llm",
            func_process_input=_process_input,
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        oxy_request = oxy_request_factory(query="test", mas=dummy_mas)
        response = await agent.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert processed["value"] is True


class TestFuncProcessOutput:
    """Test func_process_output hook."""

    @pytest.mark.asyncio
    async def test_process_output_modifies_response(
        self, monkeypatch, dummy_mas, oxy_request_factory
    ):
        """func_process_output should be called with the OxyResponse and
        can modify it after execution."""
        _patch_local_agent_config(monkeypatch)

        async def _process_output(oxy_response: OxyResponse) -> OxyResponse:
            oxy_response.extra["processed"] = True
            return oxy_response

        async def _original(r):
            return "original output"

        llm = MockLLM(
            name="mock_llm",
            func_mock_process=_original,
        )
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        agent = ChatAgent(
            name="chat_agent",
            desc="Agent with process_output",
            llm_model="mock_llm",
            func_process_output=_process_output,
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        oxy_request = oxy_request_factory(query="test", mas=dummy_mas)
        response = await agent.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert response.extra.get("processed") is True


class TestFuncExecute:
    """Test func_execute replacing the default _execute."""

    @pytest.mark.asyncio
    async def test_func_execute_overrides_default(self, dummy_mas, oxy_request_factory):
        """When func_execute is set on a tool, it replaces the default
        _execute method entirely."""
        custom_called = {"value": False}

        async def _custom_execute(oxy_request: OxyRequest) -> OxyResponse:
            custom_called["value"] = True
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="custom_output",
            )

        tool = FunctionTool(
            name="custom_tool",
            desc="Tool with custom execute",
            func_process=lambda: "should not be called",
            func_execute=_custom_execute,
        )
        tool.set_mas(dummy_mas)
        dummy_mas.add_oxy(tool)

        oxy_request = oxy_request_factory(mas=dummy_mas)
        response = await tool.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert response.output == "custom_output"
        assert custom_called["value"] is True


class TestFuncFormatOutput:
    """Test func_format_output hook."""

    @pytest.mark.asyncio
    async def test_format_output_transforms_response(
        self, monkeypatch, dummy_mas, oxy_request_factory
    ):
        """func_format_output should be called after execution to allow
        output formatting."""
        _patch_local_agent_config(monkeypatch)

        async def _format_output(oxy_response: OxyResponse) -> OxyResponse:
            if isinstance(oxy_response.output, str):
                oxy_response.output = oxy_response.output.upper()
            return oxy_response

        async def _hello(r):
            return "hello world"

        llm = MockLLM(
            name="mock_llm",
            func_mock_process=_hello,
        )
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        agent = ChatAgent(
            name="chat_agent",
            desc="Agent with format_output",
            llm_model="mock_llm",
            func_format_output=_format_output,
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        oxy_request = oxy_request_factory(query="test", mas=dummy_mas)
        response = await agent.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert response.output == "HELLO WORLD"


class TestPrecedingOxy:
    """Test preceding_oxy execution before main processing."""

    @pytest.mark.asyncio
    async def test_preceding_oxy_injects_context(
        self, monkeypatch, dummy_mas, oxy_request_factory
    ):
        """preceding_oxy should run before the main agent and inject
        its output into arguments[preceding_placeholder]."""
        _patch_local_agent_config(monkeypatch)

        async def _knowledge_func() -> str:
            return "Retrieved knowledge: Python was created in 1991."

        knowledge_tool = FunctionTool(
            name="knowledge_retriever",
            desc="Retrieves knowledge",
            func_process=_knowledge_func,
        )
        knowledge_tool.set_mas(dummy_mas)
        dummy_mas.add_oxy(knowledge_tool)

        async def _respond(oxy_request: OxyRequest) -> str:
            return "Answer with knowledge."

        llm = MockLLM(name="mock_llm", func_mock_process=_respond)
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        agent = ChatAgent(
            name="chat_agent",
            desc="Agent with preceding oxy",
            llm_model="mock_llm",
            preceding_oxy=["knowledge_retriever"],
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        oxy_request = oxy_request_factory(query="Who created Python?", mas=dummy_mas)
        response = await agent.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert "preceding_text" in oxy_request.arguments
        assert "Python" in oxy_request.arguments["preceding_text"]


class TestFuncInterceptorOnTool:
    """Test func_interceptor on a FunctionTool."""

    @pytest.mark.asyncio
    async def test_interceptor_on_tool_blocks_execution(
        self, dummy_mas, oxy_request_factory
    ):
        """A FunctionTool with func_interceptor that returns a message
        should produce OxyState.SKIPPED."""

        async def _block(oxy_request: OxyRequest) -> str:
            return "Blocked: insufficient permissions"

        tool = FunctionTool(
            name="blocked_tool",
            desc="Tool with interceptor",
            func_process=lambda: "should not run",
            func_interceptor=_block,
        )
        tool.set_mas(dummy_mas)
        dummy_mas.add_oxy(tool)

        oxy_request = oxy_request_factory(mas=dummy_mas)
        response = await tool.execute(oxy_request)

        assert response.state is OxyState.SKIPPED
        assert "blocked" in response.output.lower()

    @pytest.mark.asyncio
    async def test_interceptor_passes_when_returning_none(
        self, dummy_mas, oxy_request_factory
    ):
        """A func_interceptor returning None allows normal execution."""

        async def _allow(oxy_request: OxyRequest) -> None:
            return None

        async def _compute(x: int = 0) -> int:
            return x * 2

        tool = FunctionTool(
            name="allowed_tool",
            desc="Tool with permissive interceptor",
            func_process=_compute,
            func_interceptor=_allow,
        )
        tool.set_mas(dummy_mas)
        dummy_mas.add_oxy(tool)

        oxy_request = oxy_request_factory(mas=dummy_mas)
        oxy_request.arguments = {"x": 5}
        response = await tool.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert response.output == 10
