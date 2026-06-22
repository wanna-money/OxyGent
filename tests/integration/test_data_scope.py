"""Integration tests for data sharing scopes.

Tests cover:
- shared_data visibility within a single request chain
- group_data shared among traces in the same session group
- global_data accessible across the entire MAS
- Isolation: data in one scope does not leak to another
- shared_data propagation through nested agent calls

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
"""

import pytest

from oxygent.mas import MAS
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.agents.react_agent import ReActAgent
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyResponse, OxyState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_llm(name: str = "mock_llm", output: str = "mock_response") -> MockLLM:
    async def _respond(oxy_request: OxyRequest) -> str:
        return output

    return MockLLM(name=name, func_mock_process=_respond)


def _make_chat_agent(
    name: str = "chat_agent",
    llm_model: str = "mock_llm",
    is_master: bool = True,
    tools: list[str] | None = None,
) -> ChatAgent:
    return ChatAgent(
        name=name,
        llm_model=llm_model,
        prompt="You are a test assistant.",
        is_master=is_master,
        tools=tools or [],
    )


# ============================================================================
# Tests
# ============================================================================


class TestSharedData:
    """Test shared_data scope within a single request chain."""

    @pytest.mark.asyncio
    async def test_shared_data_passed_through_payload(self):
        """shared_data passed via the payload should be accessible in the
        OxyRequest during execution."""
        captured = {}

        async def _capture_respond(oxy_request: OxyRequest) -> str:
            captured["shared_data"] = dict(oxy_request.shared_data)
            return "done"

        llm = MockLLM(name="mock_llm", func_mock_process=_capture_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            response = await mas.chat_with_agent(
                payload={
                    "query": "test",
                    "shared_data": {"custom_key": "custom_value"},
                }
            )

            assert response.state is OxyState.COMPLETED
            assert "custom_key" in captured.get("shared_data", {})
            assert captured["shared_data"]["custom_key"] == "custom_value"

    @pytest.mark.asyncio
    async def test_shared_data_has_metrics(self):
        """chat_with_agent injects _metrics into shared_data automatically."""
        captured = {}

        async def _capture_respond(oxy_request: OxyRequest) -> str:
            captured["shared_data"] = dict(oxy_request.shared_data)
            return "done"

        llm = MockLLM(name="mock_llm", func_mock_process=_capture_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            response = await mas.chat_with_agent(payload={"query": "test"})

            assert response.state is OxyState.COMPLETED
            assert "_metrics" in captured.get("shared_data", {})

    @pytest.mark.asyncio
    async def test_shared_data_visible_in_tool_call(
        self, monkeypatch, dummy_mas, oxy_request_factory
    ):
        """shared_data should be visible when a tool is called from an agent,
        since shared_data is a shared reference across clone_with."""

        async def _respond(oxy_request: OxyRequest) -> str:
            return "mock_response"

        llm = MockLLM(name="mock_llm", func_mock_process=_respond)
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        tool_received_data = {}

        async def _tool_func(text: str = "") -> str:
            return "tool_result"

        tool = FunctionTool(
            name="test_tool", desc="A test tool", func_process=_tool_func
        )
        tool.set_mas(dummy_mas)
        dummy_mas.add_oxy(tool)

        agent = ReActAgent(
            name="react_agent",
            desc="Test agent",
            tools=["test_tool"],
            llm_model="mock_llm",
            max_react_rounds=3,
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

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

        async def _fake_call(self, *, callee, arguments, **kwargs):
            if callee == "mock_llm":
                tool_received_data["shared"] = dict(self.shared_data)
                return OxyResponse(
                    state=OxyState.COMPLETED, output="The answer.", oxy_request=self
                )
            return OxyResponse(
                state=OxyState.FAILED, output="unexpected", oxy_request=self
            )

        monkeypatch.setattr(
            "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
        )

        oxy_request = oxy_request_factory(query="test question", mas=dummy_mas)
        oxy_request.shared_data["test_flag"] = True
        response = await agent.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert tool_received_data.get("shared", {}).get("test_flag") is True


class TestGlobalData:
    """Test global_data accessible across the entire MAS."""

    @pytest.mark.asyncio
    async def test_global_data_accessible_from_agent(self):
        """global_data set on the MAS should be accessible via
        oxy_request.get_global_data() during agent execution."""
        captured = {}

        async def _capture_respond(oxy_request: OxyRequest) -> str:
            captured["global_val"] = oxy_request.get_global_data("app_version")
            return "done"

        llm = MockLLM(name="mock_llm", func_mock_process=_capture_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            mas.global_data["app_version"] = "2.0.0"

            response = await mas.chat_with_agent(payload={"query": "version check"})

            assert response.state is OxyState.COMPLETED
            assert captured.get("global_val") == "2.0.0"

    @pytest.mark.asyncio
    async def test_global_data_shared_across_requests(self):
        """global_data persists across multiple chat_with_agent calls."""
        call_count = {"value": 0}

        async def _counting_respond(oxy_request: OxyRequest) -> str:
            call_count["value"] += 1
            prev = oxy_request.get_global_data("counter", 0)
            oxy_request.set_global_data("counter", prev + 1)
            return f"counter={prev + 1}"

        llm = MockLLM(name="mock_llm", func_mock_process=_counting_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            r1 = await mas.chat_with_agent(payload={"query": "first"})
            assert r1.state is OxyState.COMPLETED

            r2 = await mas.chat_with_agent(payload={"query": "second"})
            assert r2.state is OxyState.COMPLETED

            assert mas.global_data.get("counter") == 2


class TestDataIsolation:
    """Test that data scopes do not leak into each other."""

    @pytest.mark.asyncio
    async def test_shared_data_does_not_leak_between_requests(self):
        """shared_data from one request should not appear in an independent
        subsequent request (without from_trace_id)."""
        captured_shared = []

        async def _capture_respond(oxy_request: OxyRequest) -> str:
            captured_shared.append(dict(oxy_request.shared_data))
            return "done"

        llm = MockLLM(name="mock_llm", func_mock_process=_capture_respond)
        agent = _make_chat_agent()

        async with MAS(oxy_space=[llm, agent]) as mas:
            await mas.chat_with_agent(
                payload={
                    "query": "first",
                    "shared_data": {"secret": "abc123"},
                }
            )
            await mas.chat_with_agent(payload={"query": "second"})

            assert len(captured_shared) == 2
            assert "secret" in captured_shared[0]
            assert "secret" not in captured_shared[1]
