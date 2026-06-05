"""Integration tests for OxyGent tool execution through the full Oxy lifecycle.

Each test creates tools (FunctionTool or FunctionHub), wires them into a
DummyMAS, and drives them through the complete execute() pipeline (pre_process
-> _execute -> post_process, etc.).  No external services are required.

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    mock_llm_factory, function_tool_factory, oxy_request_factory, dummy_mas
"""

import asyncio

import pytest

from oxygent.oxy.function_tools.function_hub import FunctionHub
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.schemas import OxyRequest, OxyState

# ---------------------------------------------------------------------------
# 1. FunctionTool async execution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_function_tool_async_execution(dummy_mas, oxy_request_factory):
    """FunctionTool wrapping an async function executes correctly.

    Verifies that:
      - execute returns OxyState.COMPLETED
      - output matches the expected computed value
    """

    async def add(a: int, b: int) -> int:
        return a + b

    tool = FunctionTool(name="add_tool", desc="Adds two numbers", func_process=add)
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    oxy_request = oxy_request_factory(mas=dummy_mas)
    oxy_request.arguments = {"a": 3, "b": 5}

    response = await tool.execute(oxy_request)

    assert response.state == OxyState.COMPLETED
    assert response.output == 8


# ---------------------------------------------------------------------------
# 2. FunctionTool sync execution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_function_tool_sync_execution(dummy_mas, oxy_request_factory):
    """FunctionTool wrapping a sync function executes correctly.

    FunctionHub wraps sync functions via functools.wraps to preserve the
    original signature.  We replicate that pattern here to verify that
    FunctionTool correctly handles a wrapped-sync-to-async callable.
    """
    import functools

    def multiply(x: int, y: int) -> int:
        return x * y

    # Wrap sync -> async the same way FunctionHub.tool() does: use
    # functools.wraps so that the async wrapper preserves the original
    # function's signature (needed by _extract_input_schema).
    @functools.wraps(multiply)
    async def async_multiply(*args, **kwargs):
        return multiply(*args, **kwargs)

    tool = FunctionTool(
        name="multiply_tool", desc="Multiplies two numbers", func_process=async_multiply
    )
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    oxy_request = oxy_request_factory(mas=dummy_mas)
    oxy_request.arguments = {"x": 4, "y": 7}

    response = await tool.execute(oxy_request)

    assert response.state == OxyState.COMPLETED
    assert response.output == 28


# ---------------------------------------------------------------------------
# 3. FunctionTool schema extraction
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_function_tool_schema_extraction():
    """FunctionTool extracts input_schema from function signature.

    Verifies that:
      - properties contain the correct parameter names
      - required lists only parameters without defaults
      - type annotations are captured
    """

    async def search(query: str, max_results: int = 10, exact: bool = False) -> str:
        return "results"

    tool = FunctionTool(
        name="search_tool", desc="Search for items", func_process=search
    )

    schema = tool.input_schema
    assert "properties" in schema
    assert "required" in schema

    # All three params should appear as properties
    assert "query" in schema["properties"]
    assert "max_results" in schema["properties"]
    assert "exact" in schema["properties"]

    # Only 'query' has no default, so it should be required
    assert "query" in schema["required"]
    assert "max_results" not in schema["required"]
    assert "exact" not in schema["required"]

    # Type annotations should be captured
    assert schema["properties"]["query"]["type"] == "str"
    assert schema["properties"]["max_results"]["type"] == "int"
    assert schema["properties"]["exact"]["type"] == "bool"


# ---------------------------------------------------------------------------
# 4. FunctionTool error handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_function_tool_error_handling(dummy_mas, oxy_request_factory):
    """FunctionTool wrapping a function that raises returns FAILED state.

    Verifies that:
      - execute returns OxyState.FAILED
      - the error message appears in output
    """

    async def fail_hard(value: str) -> str:
        raise ValueError(f"Invalid value: {value}")

    tool = FunctionTool(name="fail_tool", desc="Always fails", func_process=fail_hard)
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    oxy_request = oxy_request_factory(mas=dummy_mas)
    oxy_request.arguments = {"value": "bad_input"}

    response = await tool.execute(oxy_request)

    assert response.state == OxyState.FAILED
    assert "Invalid value: bad_input" in response.output


# ---------------------------------------------------------------------------
# 5. FunctionTool default arguments
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_function_tool_default_arguments(dummy_mas, oxy_request_factory):
    """FunctionTool uses default parameter values when arguments are omitted.

    Verifies that the default greeting is applied when only 'name' is provided.
    """

    async def greet(name: str, greeting: str = "Hello") -> str:
        return f"{greeting}, {name}!"

    tool = FunctionTool(name="greet_tool", desc="Greets a person", func_process=greet)
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    oxy_request = oxy_request_factory(mas=dummy_mas)
    oxy_request.arguments = {"name": "Alice"}

    response = await tool.execute(oxy_request)

    assert response.state == OxyState.COMPLETED
    assert response.output == "Hello, Alice!"


# ---------------------------------------------------------------------------
# 6. FunctionHub registration and init
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_function_hub_registration_and_init(dummy_mas):
    """FunctionHub registers functions via @fh.tool() and creates FunctionTool
    instances in the MAS on init().

    Verifies that:
      - Both registered functions appear in mas.oxy_name_to_oxy after init
      - The created entries are FunctionTool instances
      - The FunctionHub itself is also registered
    """
    fh = FunctionHub(name="test_hub", desc="Test function hub")
    fh.set_mas(dummy_mas)
    dummy_mas.add_oxy(fh)

    @fh.tool("Converts text to uppercase")
    def to_upper(text: str) -> str:
        return text.upper()

    @fh.tool("Converts text to lowercase")
    def to_lower(text: str) -> str:
        return text.lower()

    await fh.init()

    # FunctionHub should have created FunctionTool entries for both functions
    assert "to_upper" in dummy_mas.oxy_name_to_oxy
    assert "to_lower" in dummy_mas.oxy_name_to_oxy

    assert isinstance(dummy_mas.oxy_name_to_oxy["to_upper"], FunctionTool)
    assert isinstance(dummy_mas.oxy_name_to_oxy["to_lower"], FunctionTool)

    # The hub itself should also be registered
    assert "test_hub" in dummy_mas.oxy_name_to_oxy

    # Verify the created tools are functional by executing one
    upper_tool = dummy_mas.oxy_name_to_oxy["to_upper"]
    req = OxyRequest(arguments={"text": "hello"})
    req.set_mas(dummy_mas)

    response = await upper_tool.execute(req)
    assert response.state == OxyState.COMPLETED
    assert response.output == "HELLO"


# ---------------------------------------------------------------------------
# 7. Tool permission enforcement
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tool_permission_enforcement(dummy_mas, oxy_request_factory):
    """A tool with is_permission_required=True is skipped when the caller
    does not have it in permitted_tool_name_list.

    Uses OxyRequest.call() which checks permissions before executing.
    Verifies OxyState.SKIPPED is returned.
    """

    async def secret_op(data: str) -> str:
        return f"secret: {data}"

    tool = FunctionTool(
        name="secret_tool",
        desc="Restricted tool",
        func_process=secret_op,
        is_permission_required=True,
    )
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    # Create a caller agent that does NOT have 'secret_tool' in its permissions
    from oxygent.oxy.agents.chat_agent import ChatAgent

    caller_agent = ChatAgent(
        name="caller_agent",
        desc="Caller with no permissions",
        llm_model="mock_llm",
        prompt="test",
        permitted_tool_name_list=[],  # No permissions granted
    )
    caller_agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(caller_agent)

    # Build an OxyRequest that looks like it comes from caller_agent (not "user")
    oxy_request = OxyRequest(
        arguments={"data": "classified"},
        caller="caller_agent",
        caller_category="agent",
        callee="caller_agent",
        callee_category="agent",
    )
    oxy_request.set_mas(dummy_mas)
    # Simulate that we are inside caller_agent's execution context
    oxy_request.node_id = "test_node"

    response = await oxy_request.call(
        callee="secret_tool", arguments={"data": "classified"}
    )

    assert response.state == OxyState.SKIPPED
    assert "No permission" in response.output


# ---------------------------------------------------------------------------
# 8. Tool execution timeout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tool_execution_timeout(dummy_mas, oxy_request_factory):
    """A FunctionTool with a short timeout returns FAILED when the wrapped
    function exceeds the timeout.

    OxyRequest.call() wraps tool.execute() in asyncio.wait_for(timeout),
    so a slow function triggers TimeoutError -> OxyState.FAILED.
    """

    async def slow_operation(x: int) -> int:
        await asyncio.sleep(10)
        return x

    tool = FunctionTool(
        name="slow_tool",
        desc="Deliberately slow tool",
        func_process=slow_operation,
        timeout=0.1,
    )
    tool.set_mas(dummy_mas)
    dummy_mas.add_oxy(tool)

    # We need a caller in the MAS for OxyRequest.call() to look up
    from oxygent.oxy.agents.chat_agent import ChatAgent

    caller_agent = ChatAgent(
        name="timeout_caller",
        desc="Caller for timeout test",
        llm_model="mock_llm",
        prompt="test",
        permitted_tool_name_list=["slow_tool"],
    )
    caller_agent.set_mas(dummy_mas)
    dummy_mas.add_oxy(caller_agent)

    oxy_request = OxyRequest(
        arguments={"x": 42},
        caller="timeout_caller",
        caller_category="agent",
        callee="timeout_caller",
        callee_category="agent",
    )
    oxy_request.set_mas(dummy_mas)
    oxy_request.node_id = "test_node"

    response = await oxy_request.call(callee="slow_tool", arguments={"x": 42})

    assert response.state == OxyState.FAILED
    assert "timed out" in response.output.lower()
