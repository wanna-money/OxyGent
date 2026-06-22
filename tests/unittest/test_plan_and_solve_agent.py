"""Unit tests for oxygent.oxy.agents.plan_and_solve_agent (PlanAndSolveAgent)."""

import json
from unittest.mock import AsyncMock

import pytest

from oxygent.oxy.agents.plan_and_solve_agent import PlanAndSolveAgent
from oxygent.schemas import OxyRequest, OxyResponse, OxyState


# ──────────────────────────────────────────────────────────────────────────────
# Dummy MAS
# ──────────────────────────────────────────────────────────────────────────────
class DummyMAS:
    def __init__(self):
        self.oxy_name_to_oxy = {}
        self.background_tasks = {}
        self.vearch_client = AsyncMock()
        self.es_client = AsyncMock()

    def add_background_task(self, trace_id, task):
        self.background_tasks.setdefault(trace_id, set()).add(task)
        task.add_done_callback(
            lambda t: self.background_tasks.get(trace_id, set()).discard(t)
        )

    @staticmethod
    def is_agent(name):
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def patched_config(monkeypatch):
    monkeypatch.setattr(
        "oxygent.config.Config.get_agent_llm_model",
        lambda: "mock_llm",
        raising=True,
    )
    monkeypatch.setattr(
        "oxygent.config.Config.get_agent_prompt",
        lambda: "",
        raising=True,
    )
    monkeypatch.setattr(
        "oxygent.config.Config.get_vearch_config",
        lambda: {},
        raising=True,
    )


@pytest.fixture
def agent(patched_config):
    a = PlanAndSolveAgent(
        name="ps_agent",
        llm_model="mock_llm",
        planner_agent="planner",
        executor_agent="executor",
        max_replan_rounds=3,
    )
    mas = DummyMAS()
    a.set_mas(mas)
    return a


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
def test_permitted_tools_include_planner_and_executor(agent):
    assert "planner" in agent.permitted_tool_name_list
    assert "executor" in agent.permitted_tool_name_list


@pytest.mark.asyncio
async def test_straight_through_execution(agent, monkeypatch):
    """Planner returns single-step plan, executor runs it, answer is summarized."""
    req = OxyRequest(
        arguments={"query": "do task"},
        caller="user",
        caller_category="user",
        current_trace_id="t1",
    )
    req.mas = agent.mas

    async def _fake_call(self, **kw):
        callee = kw["callee"]
        if callee == "planner":
            # Must return a JSON list — agent does json.loads on it
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps(["step1"]),
                oxy_request=self,
            )
        if callee == "executor":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="executed-step1",
                oxy_request=self,
            )
        if callee == "mock_llm":
            # Single step → last step → answer() calls llm for summary
            return OxyResponse(
                state=OxyState.COMPLETED, output="final summary", oxy_request=self
            )

    monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

    resp = await agent._execute(req)
    assert resp.state is OxyState.COMPLETED
    assert "final summary" in resp.output


@pytest.mark.asyncio
async def test_complete_early(agent, monkeypatch):
    """Supervisor says complete after first step of a multi-step plan."""
    req = OxyRequest(
        arguments={"query": "quick task"},
        caller="user",
        caller_category="user",
        current_trace_id="t2",
    )
    req.mas = agent.mas

    llm_call_count = {"n": 0}

    async def _fake_call(self, **kw):
        callee = kw["callee"]
        if callee == "planner":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps(["step1", "step2"]),
                oxy_request=self,
            )
        if callee == "executor":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="executed",
                oxy_request=self,
            )
        if callee == "mock_llm":
            llm_call_count["n"] += 1
            if llm_call_count["n"] == 1:
                # Supervisor call after step1 (not last step) → "complete"
                return OxyResponse(
                    state=OxyState.COMPLETED, output="complete", oxy_request=self
                )
            # answer() call for final summary
            return OxyResponse(
                state=OxyState.COMPLETED, output="summarized", oxy_request=self
            )

    monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

    resp = await agent._execute(req)
    assert resp.state is OxyState.COMPLETED


@pytest.mark.asyncio
async def test_replan_then_complete(agent, monkeypatch):
    """Supervisor says replan, then second round has single-step plan that completes."""
    req = OxyRequest(
        arguments={"query": "complex task"},
        caller="user",
        caller_category="user",
        current_trace_id="t3",
    )
    req.mas = agent.mas

    plan_count = {"n": 0}

    async def _fake_call(self, **kw):
        callee = kw["callee"]
        if callee == "planner":
            plan_count["n"] += 1
            if plan_count["n"] == 1:
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=json.dumps(["stepA", "stepB"]),
                    oxy_request=self,
                )
            # Second plan: single step → goes directly to answer()
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps(["stepC"]),
                oxy_request=self,
            )
        if callee == "executor":
            return OxyResponse(
                state=OxyState.COMPLETED, output="done", oxy_request=self
            )
        if callee == "mock_llm":
            if plan_count["n"] == 1:
                # Supervisor after stepA → replan
                return OxyResponse(
                    state=OxyState.COMPLETED, output="replan", oxy_request=self
                )
            # answer() summary after second plan's single step
            return OxyResponse(
                state=OxyState.COMPLETED, output="final answer", oxy_request=self
            )

    monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

    resp = await agent._execute(req)
    assert resp.state is OxyState.COMPLETED
    assert plan_count["n"] >= 2
