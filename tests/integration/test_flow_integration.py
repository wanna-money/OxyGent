"""Integration tests for OxyGent flow orchestrators.

Tests cover:
- Workflow (custom function execution)
- ParallelFlow (concurrent multi-tool dispatch)
- PlanAndSolve (planner -> executor pipeline)
- Reflexion (evaluate-and-improve loop)
"""

import json

import pytest

from oxygent.oxy.flows.parallel_flow import ParallelFlow
from oxygent.oxy.flows.plan_and_solve import PlanAndSolve
from oxygent.oxy.flows.reflexion import Reflexion
from oxygent.oxy.flows.workflow import Workflow
from oxygent.schemas import OxyRequest, OxyResponse, OxyState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_flow_request(
    mas,
    flow_name: str,
    query: str = "test query",
) -> OxyRequest:
    """Build an OxyRequest wired to the given DummyMAS and targeting *flow_name*."""
    req = OxyRequest(
        arguments={"query": query},
        caller="user",
        caller_category="user",
        callee=flow_name,
    )
    req.set_mas(mas)
    return req


def _register_flow(mas, flow) -> None:
    """Register a flow (and set its mas ref) in a DummyMAS."""
    flow.set_mas(mas)
    mas.add_oxy(flow)


# ============================================================================
# Workflow tests
# ============================================================================


class TestWorkflow:
    """Tests for Workflow flow."""

    @pytest.mark.asyncio
    async def test_workflow_executes_custom_function(self, dummy_mas):
        """Workflow with a func_workflow should return COMPLETED with the function output."""

        async def my_workflow(oxy_request: OxyRequest) -> str:
            query = oxy_request.get_query()
            return f"processed: {query}"

        flow = Workflow(name="custom_wf", func_workflow=my_workflow)
        _register_flow(dummy_mas, flow)

        oxy_request = _make_flow_request(dummy_mas, "custom_wf", query="hello world")
        response = await flow._execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert response.output == "processed: hello world"

    @pytest.mark.asyncio
    async def test_workflow_fails_without_function(self, dummy_mas):
        """Workflow with func_workflow=None should return FAILED."""

        flow = Workflow(name="empty_wf", func_workflow=None)
        _register_flow(dummy_mas, flow)

        oxy_request = _make_flow_request(dummy_mas, "empty_wf")
        response = await flow._execute(oxy_request)

        assert response.state is OxyState.FAILED
        assert "no func_workflow defined" in response.output


# ============================================================================
# ParallelFlow tests
# ============================================================================


class TestParallelFlow:
    """Tests for ParallelFlow concurrent dispatch."""

    @pytest.mark.asyncio
    async def test_parallel_flow_concurrent_dispatch(self, dummy_mas, monkeypatch):
        """ParallelFlow should dispatch to every tool in permitted_tool_name_list
        and concatenate all outputs."""

        tool_names = ["tool_a", "tool_b", "tool_c"]
        expected_outputs = {
            "tool_a": "result from A",
            "tool_b": "result from B",
            "tool_c": "result from C",
        }

        flow = ParallelFlow(
            name="par_flow",
            permitted_tool_name_list=tool_names,
        )
        _register_flow(dummy_mas, flow)

        # Register stub entries so permission checks pass
        for tname in tool_names:
            dummy_mas.oxy_name_to_oxy[tname] = True  # placeholder

        async def _fake_call(self_req, **kwargs) -> OxyResponse:
            callee = kwargs.get("callee", "")
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=expected_outputs.get(callee, "unknown"),
            )

        monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

        oxy_request = _make_flow_request(
            dummy_mas, "par_flow", query="parallel question"
        )
        response = await flow._execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        for expected_text in expected_outputs.values():
            assert expected_text in response.output


# ============================================================================
# PlanAndSolve tests
# ============================================================================


class TestPlanAndSolve:
    """Tests for PlanAndSolve planning-execution pipeline."""

    @pytest.mark.asyncio
    async def test_plan_and_solve_basic_flow(self, dummy_mas, monkeypatch):
        """PlanAndSolve should call the planner, parse steps, execute each step
        via the executor, and return the final executor output."""

        plan_steps = ["step 1: gather data", "step 2: summarize findings"]
        plan_json = json.dumps({"steps": plan_steps})

        executor_results = iter(
            [
                "Data gathered successfully.",
                "Summary: all findings look good.",
            ]
        )

        call_log = []

        async def _fake_call(self_req, **kwargs) -> OxyResponse:
            callee = kwargs.get("callee", "")
            call_log.append(callee)

            if callee == "planner_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=plan_json,
                )
            elif callee == "executor_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=next(executor_results),
                )
            return OxyResponse(state=OxyState.FAILED, output="unexpected callee")

        monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

        flow = PlanAndSolve(
            name="ps_flow",
            planner_agent_name="planner_agent",
            executor_agent_name="executor_agent",
            enable_replanner=False,
        )
        _register_flow(dummy_mas, flow)

        oxy_request = _make_flow_request(
            dummy_mas, "ps_flow", query="Analyze the dataset"
        )
        response = await flow._execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        # The planner should be called first, then executor twice (once per step)
        assert call_log[0] == "planner_agent"
        assert call_log.count("executor_agent") == 2
        # Final output comes from the last executor call
        assert "Summary" in response.output or "findings" in response.output


# ============================================================================
# Reflexion tests
# ============================================================================


class TestReflexion:
    """Tests for Reflexion evaluate-and-improve loop."""

    @pytest.mark.asyncio
    async def test_reflexion_satisfactory_first_round(self, dummy_mas, monkeypatch):
        """When the reflexion agent evaluates the first answer as satisfactory,
        the flow should complete in a single round."""

        satisfactory_eval = json.dumps(
            {
                "is_satisfactory": True,
                "evaluation_reason": "The answer is accurate and complete.",
                "improvement_suggestions": "",
            }
        )

        call_log = []

        async def _fake_call(self_req, **kwargs) -> OxyResponse:
            callee = kwargs.get("callee", "")
            call_log.append(callee)

            if callee == "worker_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="The capital of France is Paris.",
                )
            elif callee == "reflexion_agent":
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=satisfactory_eval,
                )
            return OxyResponse(state=OxyState.FAILED, output="unexpected callee")

        monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

        flow = Reflexion(
            name="refl_flow",
            worker_agent="worker_agent",
            reflexion_agent="reflexion_agent",
            max_reflexion_rounds=3,
        )
        _register_flow(dummy_mas, flow)

        oxy_request = _make_flow_request(
            dummy_mas, "refl_flow", query="What is the capital of France?"
        )
        response = await flow._execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        assert "Paris" in response.output
        # Worker called once, reflexion agent called once => 1 round
        assert call_log.count("worker_agent") == 1
        assert call_log.count("reflexion_agent") == 1
        assert response.extra["reflexion_rounds"] == 1

    @pytest.mark.asyncio
    async def test_reflexion_improvement_loop(self, dummy_mas, monkeypatch):
        """When the first evaluation is unsatisfactory, the reflexion flow should
        loop: worker -> evaluate -> improve -> worker -> evaluate (satisfactory).
        This verifies the improvement loop runs exactly twice."""

        unsatisfactory_eval = json.dumps(
            {
                "is_satisfactory": False,
                "evaluation_reason": "The answer is too brief and lacks detail.",
                "improvement_suggestions": "Please provide more historical context.",
            }
        )
        satisfactory_eval = json.dumps(
            {
                "is_satisfactory": True,
                "evaluation_reason": "The answer is now thorough and well-explained.",
                "improvement_suggestions": "",
            }
        )

        worker_call_count = 0
        reflexion_call_count = 0
        call_log = []

        async def _fake_call(self_req, **kwargs) -> OxyResponse:
            nonlocal worker_call_count, reflexion_call_count
            callee = kwargs.get("callee", "")
            call_log.append(callee)

            if callee == "worker_agent":
                worker_call_count += 1
                if worker_call_count == 1:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output="Paris is the capital of France.",
                    )
                else:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output="Paris is the capital of France. It has been the capital "
                        "since the 10th century and is known for the Eiffel Tower.",
                    )

            elif callee == "reflexion_agent":
                reflexion_call_count += 1
                if reflexion_call_count == 1:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=unsatisfactory_eval,
                    )
                else:
                    return OxyResponse(
                        state=OxyState.COMPLETED,
                        output=satisfactory_eval,
                    )

            return OxyResponse(state=OxyState.FAILED, output="unexpected callee")

        monkeypatch.setattr("oxygent.schemas.oxy.OxyRequest.call", _fake_call)

        flow = Reflexion(
            name="refl_loop_flow",
            worker_agent="worker_agent",
            reflexion_agent="reflexion_agent",
            max_reflexion_rounds=5,
        )
        _register_flow(dummy_mas, flow)

        oxy_request = _make_flow_request(
            dummy_mas, "refl_loop_flow", query="What is the capital of France?"
        )
        response = await flow._execute(oxy_request)

        assert response.state is OxyState.COMPLETED
        # The improved answer should appear in the output
        assert "Eiffel Tower" in response.output
        # Worker called twice, reflexion agent called twice => 2 rounds
        assert worker_call_count == 2
        assert reflexion_call_count == 2
        assert response.extra["reflexion_rounds"] == 2
