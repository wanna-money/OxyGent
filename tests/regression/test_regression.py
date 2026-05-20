"""Regression tests guarding against known edge cases in OxyGent.

Each test targets a specific invariant or boundary condition that must
hold across future changes.  All tests use in-memory storage and MockLLM
so they can run without external services.

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
    DummyMAS, make_sequential_llm_func
"""

import asyncio
import copy
import json
from typing import Any
from unittest.mock import AsyncMock

import pytest

from oxygent.config import Config
from oxygent.oxy.agents.chat_agent import ChatAgent
from oxygent.oxy.agents.react_agent import ReActAgent
from oxygent.oxy.base_oxy import Oxy
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
        lambda: "System prompt",
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_vearch_config",
        lambda: None,
    )


class ConcreteOxy(Oxy):
    """Minimal concrete Oxy subclass for testing base-class behaviour."""

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        return OxyResponse(
            state=OxyState.COMPLETED,
            output=f"executed:{oxy_request.arguments.get('query', '')}",
        )


class SlowOxy(Oxy):
    """Oxy that sleeps in _execute, for timeout and concurrency tests."""

    sleep_seconds: float = 0.1

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        await asyncio.sleep(self.sleep_seconds)
        return OxyResponse(
            state=OxyState.COMPLETED,
            output=f"done:{oxy_request.arguments.get('id', '')}",
        )


# ===================================================================
# 1. OxyRequest.__deepcopy__ shares shared_data
# ===================================================================

class TestOxyRequestDeepCopy:

    def test_deepcopy_shares_shared_data(self):
        """Modifying shared_data on a deep-copied request must be visible
        on the original, because __deepcopy__ intentionally shares
        the reference."""
        original = OxyRequest(
            shared_data={"key": "value"},
            arguments={"query": "test"},
        )
        copied = copy.deepcopy(original)

        # Mutate through the copy
        copied.shared_data["key"] = "modified"
        copied.shared_data["new_key"] = "new_value"

        # Original must reflect the same mutations
        assert original.shared_data["key"] == "modified"
        assert original.shared_data["new_key"] == "new_value"
        assert original.shared_data is copied.shared_data

    def test_deepcopy_shares_group_data(self):
        """Same as shared_data: group_data is intentionally shared across
        deep copies."""
        original = OxyRequest(
            group_data={"session": "abc123"},
            arguments={"query": "test"},
        )
        copied = copy.deepcopy(original)

        copied.group_data["session"] = "modified_session"
        copied.group_data["extra"] = 42

        assert original.group_data["session"] == "modified_session"
        assert original.group_data["extra"] == 42
        assert original.group_data is copied.group_data

    def test_deepcopy_does_not_share_arguments(self):
        """arguments must be independent after deep copy (they are not in
        the shared-reference set)."""
        original = OxyRequest(arguments={"query": "original"})
        copied = copy.deepcopy(original)

        copied.arguments["query"] = "changed"
        assert original.arguments["query"] == "original"


# ===================================================================
# 3. OxyRequest.clone_with preserves fields
# ===================================================================

class TestOxyRequestCloneWith:

    def test_clone_with_preserves_fields(self):
        """clone_with should change only the specified fields and leave
        everything else intact."""
        original = OxyRequest(
            caller="original_caller",
            callee="original_callee",
            arguments={"query": "hello"},
            shared_data={"s": 1},
        )
        cloned = original.clone_with(caller="new_caller")

        assert cloned.caller == "new_caller"
        # Unchanged fields
        assert cloned.callee == "original_callee"
        # shared_data is the same reference (deep-copy semantics)
        assert cloned.shared_data is original.shared_data

    def test_clone_with_invalid_field_raises(self):
        """clone_with with a nonexistent field must raise AttributeError."""
        original = OxyRequest(arguments={"query": "test"})
        with pytest.raises(AttributeError, match="no attribute"):
            original.clone_with(nonexistent_field="value")


# ===================================================================
# 4. Config singleton isolation via reset_config fixture
# ===================================================================

class TestConfigSingletonIsolation:

    def test_config_mutation_is_visible(self):
        """Verify that Config changes take effect within the same test."""
        Config.set_app_name("regression_test_app")
        assert Config.get_app_name() == "regression_test_app"

    def test_config_mutation_does_not_leak(self):
        """reset_config (autouse) restores Config between tests, so the
        previous test's mutation must not be visible here."""
        assert Config.get_app_name() != "regression_test_app"


# ===================================================================
# 5. ReActAgent max_react_rounds fallback
# ===================================================================

@pytest.mark.asyncio
async def test_react_agent_max_rounds_fallback(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """When the LLM always returns tool-call JSON, the ReActAgent must stop
    after max_react_rounds and produce a fallback summary (not hang)."""
    _patch_local_agent_config(monkeypatch)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = ReActAgent(
        name="react_agent",
        desc="Max-rounds regression test",
        tools=[],
        llm_model="mock_llm",
        max_react_rounds=2,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    # Track total LLM calls to verify the agent stops.
    call_count = {"llm": 0}

    async def _fake_call(self_req, *, callee, arguments, **kwargs):
        call_count["llm"] += 1
        if callee == "mock_llm":
            # Check if this is the fallback summary call (last call after
            # exhausting rounds).  The fallback prompt contains
            # "tool execution results".
            messages = arguments.get("messages", [])
            is_fallback = any(
                "tool execution results" in str(m.get("content", "")).lower()
                for m in messages
                if isinstance(m, dict)
            )
            if is_fallback:
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="Fallback summary after max rounds.",
                    oxy_request=self_req,
                )
            # Normal round: always return a tool call so the agent never
            # stops on its own.
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=json.dumps({
                    "tool_name": "some_tool",
                    "arguments": {"query": "test"},
                }),
                oxy_request=self_req,
            )
        if callee == "some_tool":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="tool result",
                oxy_request=self_req,
            )
        return OxyResponse(
            state=OxyState.FAILED,
            output=f"Unknown callee: {callee}",
            oxy_request=self_req,
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="Run forever?", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert "Fallback summary" in response.output
    # max_react_rounds=2 means up to 3 iterations (range(max+1)),
    # each iteration = 1 LLM call + 1 tool call, then 1 fallback LLM call.
    # Total should be bounded, not infinite.
    assert call_count["llm"] <= 10, (
        f"LLM was called {call_count['llm']} times, agent did not respect max_react_rounds"
    )


# ===================================================================
# 6. ReActAgent parse error recovery
# ===================================================================

@pytest.mark.asyncio
async def test_react_agent_parse_error_recovery(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """ReActAgent receives invalid JSON first, then a valid plain-text
    answer.  It should recover from the parse error and produce the
    answer."""
    _patch_local_agent_config(monkeypatch)

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = ReActAgent(
        name="react_agent",
        desc="Parse error recovery test",
        tools=[],
        llm_model="mock_llm",
        max_react_rounds=5,
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    call_count = {"llm": 0}

    async def _fake_call(self_req, *, callee, arguments, **kwargs):
        if callee == "mock_llm":
            call_count["llm"] += 1
            if call_count["llm"] == 1:
                # First call: return broken JSON containing tool_name,
                # arguments, { and } so it triggers ERROR_PARSE.
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output='{tool_name: "bad", arguments: {broken}}',
                    oxy_request=self_req,
                )
            else:
                # Second call: return a plain-text answer (no JSON).
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output="The recovered answer.",
                    oxy_request=self_req,
                )
        return OxyResponse(
            state=OxyState.FAILED,
            output=f"Unknown callee: {callee}",
            oxy_request=self_req,
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="Parse error test", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert response.output == "The recovered answer."
    assert call_count["llm"] >= 2, "LLM should be called at least twice (error + recovery)"


# ===================================================================
# 7. ChatAgent with empty tool list
# ===================================================================

@pytest.mark.asyncio
async def test_empty_tool_list_agent(
    monkeypatch, dummy_mas, mock_llm_factory, oxy_request_factory
):
    """A ChatAgent with no tools must still work normally (no crash from
    empty tool list)."""
    _patch_local_agent_config(monkeypatch)

    expected_output = "I have no tools but I can still chat."

    llm = mock_llm_factory(name="mock_llm", response="unused")
    llm.set_mas(dummy_mas)
    dummy_mas.add_oxy(llm)

    agent = ChatAgent(
        name="chat_agent",
        desc="No-tools ChatAgent",
        llm_model="mock_llm",
        tools=[],
    )
    agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(agent)
    await agent.init()

    async def _fake_call(self_req, *, callee, arguments, **kwargs):
        if callee == "mock_llm":
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=expected_output,
                oxy_request=self_req,
            )
        return OxyResponse(
            state=OxyState.FAILED,
            output=f"Unknown callee: {callee}",
            oxy_request=self_req,
        )

    monkeypatch.setattr(
        "oxygent.schemas.oxy.OxyRequest.call", _fake_call, raising=True
    )

    oxy_request = oxy_request_factory(query="Hello?", mas=dummy_mas)
    response = await agent.execute(oxy_request)

    assert response.state is OxyState.COMPLETED
    assert response.output == expected_output


# ===================================================================
# 8. Parallel execution -- no shared-state corruption
# ===================================================================

@pytest.mark.asyncio
async def test_parallel_execution_no_shared_state_corruption():
    """Five concurrent execute() calls on the same Oxy instance must each
    produce independent, correct output with no cross-contamination."""
    oxy = ConcreteOxy(name="parallel_test", retries=1)

    async def _run(idx: int) -> OxyResponse:
        req = OxyRequest(arguments={"query": f"q{idx}", "id": str(idx)})
        return await oxy.execute(req)

    responses = await asyncio.gather(*[_run(i) for i in range(5)])

    outputs = {r.output for r in responses}
    expected = {f"executed:q{i}" for i in range(5)}
    assert outputs == expected, (
        f"Expected each task to produce its own output. Got: {outputs}"
    )
    for r in responses:
        assert r.state is OxyState.COMPLETED


# ===================================================================
# 9. Semaphore limits concurrency
# ===================================================================

@pytest.mark.asyncio
async def test_semaphore_limits_concurrency():
    """An Oxy with semaphore=2 must never have more than 2 concurrent
    _execute calls running at the same time."""
    max_concurrent = 0
    current_concurrent = 0
    lock = asyncio.Lock()

    class SemaphoreTestOxy(Oxy):
        async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
            nonlocal max_concurrent, current_concurrent
            async with lock:
                current_concurrent += 1
                if current_concurrent > max_concurrent:
                    max_concurrent = current_concurrent
            # Yield control so other tasks can attempt to enter
            await asyncio.sleep(0.05)
            async with lock:
                current_concurrent -= 1
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="ok",
            )

    oxy = SemaphoreTestOxy(name="sem_test", semaphore=2, retries=1)

    tasks = []
    for i in range(4):
        req = OxyRequest(arguments={"query": f"task_{i}"})
        tasks.append(oxy.execute(req))

    results = await asyncio.gather(*tasks)

    assert all(r.state is OxyState.COMPLETED for r in results)
    assert max_concurrent <= 2, (
        f"Expected at most 2 concurrent executions, observed {max_concurrent}"
    )
    # Ensure there was actual concurrency (not purely serial)
    assert max_concurrent == 2, (
        f"Expected 2 concurrent executions (semaphore=2), but only observed {max_concurrent}"
    )


# ===================================================================
# 10. Timeout enforcement
# ===================================================================

@pytest.mark.asyncio
async def test_timeout_enforcement():
    """An Oxy whose _execute sleeps for 10 seconds but has timeout=0.5
    must be terminated by the timeout guard in OxyRequest.call()."""

    class NeverFinishOxy(Oxy):
        async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
            await asyncio.sleep(10)
            return OxyResponse(state=OxyState.COMPLETED, output="should not reach")

    from tests.conftest import DummyMAS

    dummy_mas = DummyMAS()

    oxy = NeverFinishOxy(name="slow_oxy", timeout=0.5, retries=1)
    oxy.set_mas(dummy_mas)
    dummy_mas.add_oxy(oxy)

    # We also need a caller registered in the MAS that has permission
    caller = ConcreteOxy(
        name="caller_oxy",
        permitted_tool_name_list=["slow_oxy"],
        retries=1,
    )
    caller.set_mas(dummy_mas)
    dummy_mas.add_oxy(caller)

    req = OxyRequest(
        arguments={"query": "test timeout"},
        caller="caller_oxy",
        callee="slow_oxy",
        caller_category="agent",
    )
    req.set_mas(dummy_mas)

    # Use OxyRequest.call which wraps execute with asyncio.wait_for(timeout)
    response = await req.call(callee="slow_oxy", arguments={"query": "test timeout"})

    assert response.state is OxyState.FAILED
    assert "timed out" in response.output.lower()


# ===================================================================
# 11. Permission enforcement skips unauthorized callee
# ===================================================================

@pytest.mark.asyncio
async def test_permission_enforcement_skips_unauthorized():
    """When a tool has is_permission_required=True and the caller has not
    added it to permitted_tool_name_list, OxyRequest.call must return
    OxyState.SKIPPED."""
    from oxygent.oxy.base_tool import BaseTool
    from tests.conftest import DummyMAS

    dummy_mas = DummyMAS()

    class SimpleTool(BaseTool):
        async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
            return OxyResponse(state=OxyState.COMPLETED, output="tool ran")

    tool = SimpleTool(
        name="restricted_tool",
        desc="A restricted tool",
        is_permission_required=True,
    )
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    # Caller that does NOT have restricted_tool in its permitted list
    caller = ConcreteOxy(
        name="unprivileged_caller",
        category="agent",
        permitted_tool_name_list=[],
        retries=1,
    )
    caller.set_mas(dummy_mas)
    dummy_mas.add_oxy(caller)

    req = OxyRequest(
        arguments={"query": "do something"},
        caller="unprivileged_caller",
        callee="restricted_tool",
        caller_category="agent",
        callee_category="tool",
    )
    req.set_mas(dummy_mas)

    response = await req.call(
        callee="restricted_tool",
        arguments={"query": "do something"},
    )

    assert response.state is OxyState.SKIPPED
    assert "no permission" in response.output.lower()


# ===================================================================
# 12. preceding_oxy injection
# ===================================================================

@pytest.mark.asyncio
async def test_preceding_oxy_injection(monkeypatch):
    """An Oxy with preceding_oxy=["preprocessor"] must run the
    preprocessor before _execute and inject its output into
    arguments[preceding_placeholder]."""
    from tests.conftest import DummyMAS

    dummy_mas = DummyMAS()

    # The preprocessor Oxy that returns known output
    class Preprocessor(Oxy):
        async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="preprocessed_data",
            )

    preprocessor = Preprocessor(name="preprocessor", retries=1)
    preprocessor.set_mas(dummy_mas)
    dummy_mas.add_oxy(preprocessor)

    # Track what arguments the main Oxy receives at _execute time
    captured_args: dict[str, Any] = {}

    class MainOxy(Oxy):
        async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
            captured_args.update(oxy_request.arguments)
            return OxyResponse(
                state=OxyState.COMPLETED,
                output="main_done",
            )

    main_oxy = MainOxy(
        name="main_oxy",
        preceding_oxy=["preprocessor"],
        retries=1,
    )
    main_oxy.set_mas(dummy_mas)
    dummy_mas.add_oxy(main_oxy)

    # The main oxy needs the caller registered too (for permission in call)
    caller_oxy = ConcreteOxy(
        name="user",
        category="user",
        permitted_tool_name_list=["preprocessor", "main_oxy"],
        retries=1,
    )
    caller_oxy.set_mas(dummy_mas)
    dummy_mas.add_oxy(caller_oxy)

    req = OxyRequest(
        arguments={"query": "test preceding"},
        caller="user",
        caller_category="user",
    )
    req.set_mas(dummy_mas)

    response = await main_oxy.execute(req)

    assert response.state is OxyState.COMPLETED
    assert response.output == "main_done"
    # The preceding_placeholder defaults to "preceding_text"
    assert "preceding_text" in captured_args, (
        f"preceding_text not found in arguments. Keys: {list(captured_args.keys())}"
    )
    assert "preprocessed_data" in captured_args["preceding_text"]
