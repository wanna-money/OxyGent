"""Integration tests for OxyGent agents through the full Oxy.execute() lifecycle.

Each test creates agents with MockLLM and in-memory storage, wires them into
a DummyMAS, and drives them through the complete execute() pipeline (pre_process
-> _execute -> post_process, etc.).  No external services are required.

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
    make_react_llm_func, make_sequential_llm_func
"""

import json

import pytest

from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.agents.parallel_agent import ParallelAgent
from oxygent.oxy.agents.rag_agent import RAGAgent
from oxygent.oxy.agents.react_agent import ReActAgent
from oxygent.oxy.agents.workflow_agent import WorkflowAgent
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyResponse, OxyState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_local_agent_config(monkeypatch):
    """Patch Config classmethods that LocalAgent reads at construction time."""
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


# ---------------------------------------------------------------------------
# 1. ChatAgent full lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_chat_agent_full_lifecycle(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """ChatAgent + MockLLM through the complete execute() pipeline.

    Verifies that:
      - set_mas and init succeed
      - execute returns OxyState.COMPLETED
      - output matches the MockLLM response
    """
    _patch_local_agent_config(monkeypatch)

    expected_answer = "Hello! I am your assistant."

    llm = mock_llm_factory(name="mock_llm", response=expected_answer)
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = ChatAgent(
        name="chat_agent",
        desc="Integration test ChatAgent",
        llm_model="mock_llm",
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    oxy_request = oxy_request_factory(query="Hi there!", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert response.output == expected_answer


# ---------------------------------------------------------------------------
# 2. ReActAgent -- tool call then answer
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_react_agent_tool_call_and_answer(
    monkeypatch, dummy_mas, mock_llm_factory, function_tool_factory, oxy_request_factory
):
    """ReActAgent calls a tool, receives the observation, then returns an answer.

    The mock LLM returns a tool-call JSON on the first call and a plain-text
    answer on the second call (after observing the tool result).  We patch
    OxyRequest.call so we can control the exact responses.
    """
    _patch_local_agent_config(monkeypatch)

    tool = function_tool_factory(
        name="calculator",
        desc="A calculator tool",
        func=lambda x="0", y="0": f"{int(x) + int(y)}",
    )
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = ReActAgent(
        name="react_agent",
        desc="Integration test ReActAgent",
        tools=["calculator"],
        llm_model="mock_llm",
        max_react_rounds=5,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    # Track the number of LLM calls to alternate responses.
    call_count = {"llm": 0, "tool": 0}

    async def _fake_call(self, *, callee, arguments, **kwargs):
        if callee == "mock_llm":
            call_count["llm"] += 1
            if call_count["llm"] == 1:
                # First LLM call: request a tool call
                tool_call_json = json.dumps(
                    {"tool_name": "calculator", "arguments": {"x": "3", "y": "4"}}
                )
                return OxyResponse(
                    state=OxyState.COMPLETED, output=tool_call_json, oxy_request=self
                )
            else:
                # Second LLM call: return the final answer
                return OxyResponse(
                    state=OxyState.COMPLETED, output="The answer is 7.", oxy_request=self
                )
        elif callee == "calculator":
            call_count["tool"] += 1
            return OxyResponse(
                state=OxyState.COMPLETED, output="7", oxy_request=self
            )
        return OxyResponse(
            state=OxyState.FAILED, output=f"Unknown callee: {callee}", oxy_request=self
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="What is 3 + 4?", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert response.output == "The answer is 7."
    assert call_count["llm"] >= 2, "LLM should have been called at least twice"
    assert call_count["tool"] >= 1, "Tool should have been called at least once"


# ---------------------------------------------------------------------------
# 3. ReActAgent -- direct answer (no tool call)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_react_agent_direct_answer(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """ReActAgent returns immediately when the LLM produces plain text (no JSON).

    No tools should be invoked.
    """
    _patch_local_agent_config(monkeypatch)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = ReActAgent(
        name="react_agent",
        desc="Integration test ReActAgent direct answer",
        tools=[],
        llm_model="mock_llm",
        max_react_rounds=5,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    plain_answer = "Paris is the capital of France."

    async def _fake_call(self, *, callee, arguments, **kwargs):
        if callee == "mock_llm":
            return OxyResponse(
                state=OxyState.COMPLETED, output=plain_answer, oxy_request=self
            )
        return OxyResponse(
            state=OxyState.FAILED, output="should not be called", oxy_request=self
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="What is the capital of France?", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert response.output == plain_answer


# ---------------------------------------------------------------------------
# 4. ParallelAgent -- concurrent execution of sub-agents
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parallel_agent_concurrent_execution(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """ParallelAgent dispatches to two ChatAgent sub-agents concurrently.

    After both sub-agents reply, the ParallelAgent asks the LLM to summarize.
    We verify all sub-agents are called and the summary is returned.
    """
    _patch_local_agent_config(monkeypatch)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    sub_agent_a = ChatAgent(
        name="expert_a",
        desc="Expert A",
        llm_model="mock_llm",
    )
    sub_agent_a.set_mas(dummy_mas)
    dummy_mas.add_oxy(sub_agent_a)

    sub_agent_b = ChatAgent(
        name="expert_b",
        desc="Expert B",
        llm_model="mock_llm",
    )
    sub_agent_b.set_mas(dummy_mas)
    dummy_mas.add_oxy(sub_agent_b)

    parallel_agent = ParallelAgent(
        name="parallel_agent",
        desc="Integration test ParallelAgent",
        llm_model="mock_llm",
        permitted_tool_name_list=["expert_a", "expert_b"],
    )
    parallel_agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(parallel_agent)
    await parallel_agent.init()

    called_agents = set()

    async def _fake_call(self, *, callee, arguments, **kwargs):
        if callee == "expert_a":
            called_agents.add("expert_a")
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="Analysis from expert A.",
                oxy_request=self,
            )
        if callee == "expert_b":
            called_agents.add("expert_b")
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="Analysis from expert B.",
                oxy_request=self,
            )
        if callee == "mock_llm":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="Combined summary of both experts.",
                oxy_request=self,
            )
        return OxyResponse(
            state=OxyState.FAILED, output=f"Unknown callee: {callee}", oxy_request=self
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="Analyze this topic", mas=dummy_mas)
    response = await parallel_agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert "expert_a" in called_agents, "Expert A should have been called"
    assert "expert_b" in called_agents, "Expert B should have been called"
    assert response.output == "Combined summary of both experts."


# ---------------------------------------------------------------------------
# 5. WorkflowAgent -- with custom function
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_workflow_agent_with_custom_function(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """WorkflowAgent executes a user-defined async workflow function.

    Verifies the custom function is called and its output is returned.
    """
    _patch_local_agent_config(monkeypatch)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    workflow_called = {"value": False}

    async def custom_workflow(oxy_request: OxyRequest) -> str:
        workflow_called["value"] = True
        query = oxy_request.get_query()
        return f"Processed: {query}"

    agent = WorkflowAgent(
        name="workflow_agent",
        desc="Integration test WorkflowAgent",
        llm_model="mock_llm",
        func_workflow=custom_workflow,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    oxy_request = oxy_request_factory(query="Run my workflow", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert workflow_called["value"] is True, "Workflow function should have been called"
    assert response.output == "Processed: Run my workflow"


# ---------------------------------------------------------------------------
# 6. WorkflowAgent -- without function (expect FAILED)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_workflow_agent_without_function(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """WorkflowAgent with func_workflow=None returns OxyState.FAILED."""
    _patch_local_agent_config(monkeypatch)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = WorkflowAgent(
        name="workflow_agent_no_func",
        desc="Integration test WorkflowAgent without function",
        llm_model="mock_llm",
        func_workflow=None,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    oxy_request = oxy_request_factory(query="Should fail", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.FAILED
    assert "no func_workflow" in response.output.lower()


# ---------------------------------------------------------------------------
# 7. RAGAgent -- knowledge injection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rag_agent_knowledge_injection(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """RAGAgent calls func_retrieve_knowledge and injects context into the prompt.

    We verify that:
      - The retrieve function is called
      - The knowledge placeholder is populated in the request arguments
      - The agent completes successfully with the LLM answer
    """
    _patch_local_agent_config(monkeypatch)

    expected_knowledge = "Python was created by Guido van Rossum in 1991."
    retrieve_called = {"value": False}

    async def mock_retrieve_knowledge(oxy_request: OxyRequest) -> str:
        retrieve_called["value"] = True
        return expected_knowledge

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = RAGAgent(
        name="rag_agent",
        desc="Integration test RAGAgent",
        llm_model="mock_llm",
        func_retrieve_knowledge=mock_retrieve_knowledge,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    # Track what arguments the LLM receives so we can verify knowledge injection.
    captured_llm_args = {}

    async def _fake_call(self, *, callee, arguments, **kwargs):
        if callee == "mock_llm":
            captured_llm_args.update(arguments)
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="Python was created by Guido van Rossum.",
                oxy_request=self,
            )
        return OxyResponse(
            state=OxyState.FAILED, output=f"Unknown callee: {callee}", oxy_request=self
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="Who created Python?", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert retrieve_called["value"] is True, "Retrieve function should have been called"
    # The knowledge placeholder should have been injected into the request
    # arguments during _pre_process, which then flows into _build_instruction.
    assert oxy_request.arguments.get("knowledge") == expected_knowledge
    assert response.state is OxyState.COMPLETED
    assert "Guido van Rossum" in response.output
