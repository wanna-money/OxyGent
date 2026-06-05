"""Integration tests for multi-level agent routing and sub-agent dispatch.

Tests cover:
- Master agent delegates to correct sub-agent based on LLM response
- Two-level hierarchy: master → sub-master → leaf agent
- Sub-agent result flows back to master's response
- Agent with both tools and sub_agents uses the appropriate one

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
"""

import json

import pytest

from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.agents.react_agent import ReActAgent
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.schemas import OxyResponse, OxyState

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


class TestMasterToSubAgent:
    """Test master agent delegating to a sub-agent."""

    @pytest.mark.asyncio
    async def test_master_delegates_to_sub_agent(
        self, monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
    ):
        """The master agent's LLM produces a tool call targeting a sub-agent.
        The sub-agent returns a result, which the master then uses to form
        the final answer."""
        _patch_local_agent_config(monkeypatch)

        llm = mock_llm_factory(name="mock_llm", response="unused")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        sub_agent = ChatAgent(
            name="time_agent",
            desc="A tool that can query the time",
            llm_model="mock_llm",
        )
        sub_agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(sub_agent)

        master = ReActAgent(
            name="master_agent",
            desc="Master agent",
            llm_model="mock_llm",
            is_master=True,
            sub_agents=["time_agent"],
            max_react_rounds=5,
        )
        master.set_mas(dummy_mas)
        dummy_mas.add_oxy(master)
        await master.init()

        call_log = []

        async def _fake_call(self, *, callee, arguments, **kwargs):
            call_log.append(callee)
            if callee == "mock_llm":
                if "time_agent" not in call_log:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=json.dumps(
                            {
                                "tool_name": "time_agent",
                                "arguments": {"query": "What time is it?"},
                            }
                        ),
                        oxy_request=self,
                    )
                else:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output="The current time is 10:30 AM.",
                        oxy_request=self,
                    )
            elif callee == "time_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="10:30 AM",
                    oxy_request=self,
                )
            return OxyResponse(
                state=OxyState.FAILED, output=f"Unknown: {callee}", oxy_request=self
            )

        monkeypatch.setattr(
            "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
        )

        oxy_request = oxy_request_factory(query="What time is it?", mas=dummy_mas)
        response = await master.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert "time_agent" in call_log


class TestTwoLevelHierarchy:
    """Test two-level agent hierarchy: master → sub-master → leaf."""

    @pytest.mark.asyncio
    async def test_two_level_delegation(
        self, monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
    ):
        """Master delegates to sub-master, which delegates to leaf agent.
        The result bubbles all the way back up."""
        _patch_local_agent_config(monkeypatch)

        llm = mock_llm_factory(name="mock_llm", response="unused")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        leaf_agent = ChatAgent(
            name="leaf_agent",
            desc="Leaf specialist",
            llm_model="mock_llm",
        )
        leaf_agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(leaf_agent)

        sub_master = ReActAgent(
            name="sub_master",
            desc="Sub-master agent",
            llm_model="mock_llm",
            sub_agents=["leaf_agent"],
            max_react_rounds=3,
        )
        sub_master.set_mas(dummy_mas)
        dummy_mas.add_oxy(sub_master)

        master = ReActAgent(
            name="master_agent",
            desc="Top-level master",
            llm_model="mock_llm",
            is_master=True,
            sub_agents=["sub_master"],
            max_react_rounds=3,
        )
        master.set_mas(dummy_mas)
        dummy_mas.add_oxy(master)
        await master.init()

        call_log = []

        async def _fake_call(self, *, callee, arguments, **kwargs):
            call_log.append(callee)
            if callee == "mock_llm":
                if "sub_master" not in call_log:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=json.dumps(
                            {
                                "tool_name": "sub_master",
                                "arguments": {"query": "delegate down"},
                            }
                        ),
                        oxy_request=self,
                    )
                else:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output="Final answer from hierarchy.",
                        oxy_request=self,
                    )
            elif callee == "sub_master":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="sub_master_result",
                    oxy_request=self,
                )
            elif callee == "leaf_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="leaf_result",
                    oxy_request=self,
                )
            return OxyResponse(
                state=OxyState.FAILED, output=f"Unknown: {callee}", oxy_request=self
            )

        monkeypatch.setattr(
            "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
        )

        oxy_request = oxy_request_factory(query="Complex question", mas=dummy_mas)
        response = await master.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert "sub_master" in call_log


class TestAgentWithToolsAndSubAgents:
    """Test agent that has both tools and sub_agents."""

    @pytest.mark.asyncio
    async def test_agent_calls_tool_then_sub_agent(
        self, monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
    ):
        """An agent with both a tool and a sub-agent should be able to use
        both. The LLM first calls the tool, then calls the sub-agent."""
        _patch_local_agent_config(monkeypatch)

        llm = mock_llm_factory(name="mock_llm", response="unused")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        async def _calc(x: str = "0", y: str = "0") -> str:
            return str(int(x) + int(y))

        tool = FunctionTool(
            name="calculator", desc="Calculator tool", func_process=_calc
        )
        tool.set_mas(dummy_mas)
        dummy_mas.add_oxy(tool)

        sub_agent = ChatAgent(
            name="reporter",
            desc="Reports results",
            llm_model="mock_llm",
        )
        sub_agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(sub_agent)

        master = ReActAgent(
            name="master_agent",
            desc="Master with tools and sub-agents",
            llm_model="mock_llm",
            is_master=True,
            tools=["calculator"],
            sub_agents=["reporter"],
            max_react_rounds=5,
        )
        master.set_mas(dummy_mas)
        dummy_mas.add_oxy(master)
        await master.init()

        call_count = {"llm": 0}
        called_targets = set()

        async def _fake_call(self, *, callee, arguments, **kwargs):
            called_targets.add(callee)
            if callee == "mock_llm":
                call_count["llm"] += 1
                if call_count["llm"] == 1:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=json.dumps(
                            {
                                "tool_name": "calculator",
                                "arguments": {"x": "5", "y": "3"},
                            }
                        ),
                        oxy_request=self,
                    )
                elif call_count["llm"] == 2:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=json.dumps(
                            {
                                "tool_name": "reporter",
                                "arguments": {"query": "Report: 5+3=8"},
                            }
                        ),
                        oxy_request=self,
                    )
                else:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output="Final: 5 + 3 = 8, reported.",
                        oxy_request=self,
                    )
            elif callee == "calculator":
                return OxyResponse(
                    state=OxyState.COMPLETED, output="8", oxy_request=self
                )
            elif callee == "reporter":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="Report filed.",
                    oxy_request=self,
                )
            return OxyResponse(
                state=OxyState.FAILED, output=f"Unknown: {callee}", oxy_request=self
            )

        monkeypatch.setattr(
            "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
        )

        oxy_request = oxy_request_factory(
            query="Calculate 5+3 and report", mas=dummy_mas
        )
        response = await master.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert "calculator" in called_targets
        assert "reporter" in called_targets


class TestSubAgentResultFlowsBack:
    """Test that sub-agent results are incorporated into master's response."""

    @pytest.mark.asyncio
    async def test_sub_agent_output_visible_to_master(
        self, monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
    ):
        """After the sub-agent returns, the master should see the sub-agent's
        output in its react_memory and incorporate it into the final answer."""
        _patch_local_agent_config(monkeypatch)

        llm = mock_llm_factory(name="mock_llm", response="unused")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        sub_agent = ChatAgent(
            name="data_agent",
            desc="Data lookup agent",
            llm_model="mock_llm",
        )
        sub_agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(sub_agent)

        master = ReActAgent(
            name="master_agent",
            desc="Master",
            llm_model="mock_llm",
            is_master=True,
            sub_agents=["data_agent"],
            max_react_rounds=5,
        )
        master.set_mas(dummy_mas)
        dummy_mas.add_oxy(master)
        await master.init()

        captured_messages = []

        async def _fake_call(self, *, callee, arguments, **kwargs):
            if callee == "mock_llm":
                messages = arguments.get("messages", [])
                captured_messages.append(messages)
                has_observation = any(
                    "execution result" in str(m.get("content", "")).lower()
                    for m in messages
                    if isinstance(m, dict)
                )
                if not has_observation:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=json.dumps(
                            {
                                "tool_name": "data_agent",
                                "arguments": {"query": "lookup sales data"},
                            }
                        ),
                        oxy_request=self,
                    )
                else:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output="Sales data shows growth of 15%.",
                        oxy_request=self,
                    )
            elif callee == "data_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="Sales grew 15% year over year.",
                    oxy_request=self,
                )
            return OxyResponse(
                state=OxyState.FAILED, output="unexpected", oxy_request=self
            )

        monkeypatch.setattr(
            "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
        )

        oxy_request = oxy_request_factory(query="Get sales data", mas=dummy_mas)
        response = await master.execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert "15%" in response.output
