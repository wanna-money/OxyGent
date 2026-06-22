"""Unit tests for oxygent.oxy.llms.mock_llm (MockLLM)."""

import pytest

from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest, OxyState


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_llm():
    return MockLLM(name="test_mock")


@pytest.fixture
def oxy_request():
    return OxyRequest(
        arguments={"query": "hello"},
        caller="user",
        caller_category="user",
    )


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_default_mock_returns_output(mock_llm, oxy_request):
    """Default func_mock_process returns 'output' after sleeping."""
    resp = await mock_llm._execute(oxy_request)
    assert resp.state is OxyState.COMPLETED
    assert resp.output == "output"


@pytest.mark.asyncio
async def test_custom_mock_process(oxy_request):
    """Custom func_mock_process is used when provided."""

    async def custom_fn(req):
        return f"custom-{req.arguments['query']}"

    llm = MockLLM(name="custom_mock", func_mock_process=custom_fn)
    resp = await llm._execute(oxy_request)
    assert resp.state is OxyState.COMPLETED
    assert resp.output == "custom-hello"


def test_mock_llm_has_default_func():
    llm = MockLLM(name="m")
    assert llm.func_mock_process is not None
    assert callable(llm.func_mock_process)
