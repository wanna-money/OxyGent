"""Unit tests for PlanAndSolve Flow."""

import json
from unittest.mock import AsyncMock

import pytest

from oxygent.oxy.flows.plan_and_solve import PlanAndSolve
from oxygent.schemas import OxyRequest, OxyResponse, OxyState


async def _identity_process_message(dict_message, oxy_request):
    return dict_message


# ──────────────────────────────────────────────────────────────────────────────
# Dummy MAS
# ──────────────────────────────────────────────────────────────────────────────
class DummyMAS:
    def __init__(self):
        self.oxy_name_to_oxy = {}
        self.background_tasks = {}
        self.message_prefix = "msg"
        self.name = "test_mas"
        self.send_message = AsyncMock()
        self.func_process_message = _identity_process_message

    def add_background_task(self, trace_id, task):
        self.background_tasks.setdefault(trace_id, set()).add(task)
        task.add_done_callback(
            lambda t: self.background_tasks.get(trace_id, set()).discard(t)
        )

    def add_oxy(self, oxy):
        self.oxy_name_to_oxy[oxy.name] = oxy


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mas_env():
    return DummyMAS()


@pytest.fixture
def flow_preplan(mas_env):
    f = PlanAndSolve(
        name="ps_flow",
        desc="UT plan solve",
        pre_plan_steps=["step1", "step2"],
        executor_agent_name="executor_agent",
        llm_model="mock_llm",
    )
    f.set_mas(mas_env)
    return f


@pytest.fixture
def flow_full(mas_env):
    """Flow using default pydantic_parser_planner (parses Plan from JSON)."""
    f = PlanAndSolve(
        name="ps_flow",
        desc="UT planner first",
        executor_agent_name="executor_agent",
        planner_agent_name="planner_agent",
        llm_model="mock_llm",
    )
    f.set_mas(mas_env)
    return f


@pytest.fixture
def flow_replanner(mas_env):
    """Flow with replanner enabled, using default pydantic parsers."""
    f = PlanAndSolve(
        name="ps_flow",
        desc="UT replanner",
        executor_agent_name="executor_agent",
        planner_agent_name="planner_agent",
        enable_replanner=True,
        replanner_agent_name="replanner_agent",
        llm_model="mock_llm",
        max_replan_rounds=5,
    )
    f.set_mas(mas_env)
    return f


@pytest.fixture
def oxy_request(monkeypatch, mas_env):
    req = OxyRequest(
        arguments={"query": "What is the plan?"},
        caller="user",
        caller_category="user",
        current_trace_id="trace123",
    )
    req.mas = mas_env

    async def _fake_call(self, *, callee: str, arguments: dict, **kwargs):
        if callee == "executor_agent":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=f"done({arguments['query']})",
                oxy_request=self,
            )
        if callee == "planner_agent":
            # Return JSON that PydanticOutputParser(output_cls=Plan) can parse
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps({"steps": ["step1", "step2"]}),
                oxy_request=self,
            )
        if callee == "replanner_agent":
            # Return JSON that PydanticOutputParser(output_cls=Action) can parse
            # Action.action is Union[Response, Plan]; a Response has a "response" field
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps({"action": {"response": "final-answer"}}),
                oxy_request=self,
            )
        if callee == "mock_llm":
            return OxyResponse(
                state=OxyState.COMPLETED, output="llm-fallback", oxy_request=self
            )

    monkeypatch.setattr("oxygent.schemas.OxyRequest.call", _fake_call, raising=True)
    return req


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_execute_with_preplan(flow_preplan, oxy_request):
    """Pre-defined steps are executed without calling the planner agent."""
    resp = await flow_preplan.execute(oxy_request)
    assert resp.state is OxyState.COMPLETED
    assert "step2" in resp.output


@pytest.mark.asyncio
async def test_execute_with_planner(flow_full, oxy_request):
    """Planner agent generates a plan, executor runs each step."""
    resp = await flow_full.execute(oxy_request)
    assert resp.state is OxyState.COMPLETED
    assert "step2" in resp.output


@pytest.mark.asyncio
async def test_execute_with_replanner(flow_replanner, oxy_request):
    """Replanner returns a Response action, ending the loop."""
    resp = await flow_replanner.execute(oxy_request)
    assert resp.state is OxyState.COMPLETED
    assert "final-answer" in resp.output


@pytest.mark.asyncio
async def test_replanner_continues_with_new_plan(monkeypatch, mas_env):
    """Replanner returns a new Plan, then on second round returns Response."""
    f = PlanAndSolve(
        name="ps_flow",
        desc="UT replanner replan",
        executor_agent_name="executor_agent",
        planner_agent_name="planner_agent",
        enable_replanner=True,
        replanner_agent_name="replanner_agent",
        llm_model="mock_llm",
        max_replan_rounds=5,
    )
    f.set_mas(mas_env)

    req = OxyRequest(
        arguments={"query": "multi-replan task"},
        caller="user",
        caller_category="user",
        current_trace_id="trace456",
    )
    req.mas = mas_env

    replan_call_count = 0

    async def _fake_call(self, *, callee: str, arguments: dict, **kwargs):
        nonlocal replan_call_count
        if callee == "executor_agent":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=f"executed({arguments['query']})",
                oxy_request=self,
            )
        if callee == "planner_agent":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps({"steps": ["taskA"]}),
                oxy_request=self,
            )
        if callee == "replanner_agent":
            replan_call_count += 1
            if replan_call_count == 1:
                # First replan: return a new plan
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=json.dumps({"action": {"steps": ["taskB"]}}),
                    oxy_request=self,
                )
            # Second replan: return final response
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps({"action": {"response": "all-done"}}),
                oxy_request=self,
            )
        if callee == "mock_llm":
            return OxyResponse(
                state=OxyState.COMPLETED, output="llm-out", oxy_request=self
            )

    monkeypatch.setattr("oxygent.schemas.OxyRequest.call", _fake_call, raising=True)

    resp = await f.execute(req)
    assert resp.state is OxyState.COMPLETED
    assert "all-done" in resp.output
    assert replan_call_count == 2
