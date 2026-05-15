"""Unit tests for oxygent.oxy.api_tools.http_tool (HttpTool)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from oxygent.oxy.api_tools.http_tool import HttpTool
from oxygent.schemas import OxyRequest, OxyState


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _make_tool(**overrides):
    defaults = {
        "name": "test_http",
        "desc": "test",
        "url": "http://example.com/api",
        "method": "GET",
    }
    defaults.update(overrides)
    return HttpTool(**defaults)


def _make_request(**args):
    return OxyRequest(
        arguments=args or {"q": "test"},
        caller="user",
        caller_category="user",
    )


def _mock_httpx_client(monkeypatch, response_text="ok"):
    """Patch httpx.AsyncClient to return a mock with configurable response."""
    mock_response = MagicMock()
    mock_response.text = response_text

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    mock_client.patch.return_value = mock_response
    mock_client.request.return_value = mock_response

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_client
    mock_ctx.__aexit__.return_value = False

    monkeypatch.setattr(
        "oxygent.oxy.api_tools.http_tool.httpx.AsyncClient",
        lambda **kwargs: mock_ctx,
    )
    return mock_client


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_request(monkeypatch):
    client = _mock_httpx_client(monkeypatch, "get-response")
    tool = _make_tool(method="GET")
    req = _make_request(q="hello")

    resp = await tool._execute(req)
    assert resp.state is OxyState.COMPLETED
    assert resp.output == "get-response"
    client.get.assert_called_once()


@pytest.mark.asyncio
async def test_post_request(monkeypatch):
    client = _mock_httpx_client(monkeypatch, "post-response")
    tool = _make_tool(method="POST")
    req = _make_request(data="payload")

    resp = await tool._execute(req)
    assert resp.state is OxyState.COMPLETED
    assert resp.output == "post-response"
    client.post.assert_called_once()


@pytest.mark.asyncio
async def test_put_request(monkeypatch):
    client = _mock_httpx_client(monkeypatch, "put-response")
    tool = _make_tool(method="PUT")
    req = _make_request(data="payload")

    resp = await tool._execute(req)
    client.put.assert_called_once()


@pytest.mark.asyncio
async def test_delete_request(monkeypatch):
    client = _mock_httpx_client(monkeypatch, "del-response")
    tool = _make_tool(method="DELETE")
    req = _make_request(id="123")

    resp = await tool._execute(req)
    client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_patch_request(monkeypatch):
    client = _mock_httpx_client(monkeypatch, "patch-response")
    tool = _make_tool(method="PATCH")
    req = _make_request(field="value")

    resp = await tool._execute(req)
    client.patch.assert_called_once()


@pytest.mark.asyncio
async def test_unknown_method_falls_through(monkeypatch):
    client = _mock_httpx_client(monkeypatch, "custom-response")
    tool = _make_tool(method="OPTIONS")
    req = _make_request()

    resp = await tool._execute(req)
    assert resp.output == "custom-response"
    client.request.assert_called_once()


@pytest.mark.asyncio
async def test_default_params_merged(monkeypatch):
    client = _mock_httpx_client(monkeypatch)
    tool = _make_tool(method="GET", default_params={"token": "abc"})
    req = _make_request(q="hello")

    await tool._execute(req)
    call_kwargs = client.get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
    assert params["token"] == "abc"
    assert params["q"] == "hello"


@pytest.mark.asyncio
async def test_request_args_override_defaults(monkeypatch):
    client = _mock_httpx_client(monkeypatch)
    tool = _make_tool(method="GET", default_params={"key": "default"})
    req = _make_request(key="override")

    await tool._execute(req)
    call_kwargs = client.get.call_args
    params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
    assert params["key"] == "override"
