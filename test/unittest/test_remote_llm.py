"""Unit tests for oxygent.oxy.llms.remote_llm (RemoteLLM field validators)."""

import pytest
from pydantic import ValidationError

from oxygent.oxy.llms.remote_llm import RemoteLLM


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _make_llm(**overrides):
    """Build a RemoteLLM with valid defaults, applying overrides."""
    defaults = {
        "name": "test_llm",
        "base_url": "http://example.com",
        "model_name": "test-model",
    }
    defaults.update(overrides)
    return RemoteLLM(**defaults)


# ──────────────────────────────────────────────────────────────────────────────
# base_url validation
# ──────────────────────────────────────────────────────────────────────────────
def test_base_url_valid():
    llm = _make_llm(base_url="http://api.example.com")
    assert llm.base_url == "http://api.example.com"


def test_base_url_none_raises():
    with pytest.raises(ValidationError, match="base_url"):
        _make_llm(base_url=None)


def test_base_url_empty_raises():
    with pytest.raises(ValidationError, match="base_url"):
        _make_llm(base_url="")


def test_base_url_whitespace_raises():
    with pytest.raises(ValidationError, match="base_url"):
        _make_llm(base_url="   ")


# ──────────────────────────────────────────────────────────────────────────────
# model_name validation
# ──────────────────────────────────────────────────────────────────────────────
def test_model_name_valid():
    llm = _make_llm(model_name="gpt-4")
    assert llm.model_name == "gpt-4"


def test_model_name_none_raises():
    with pytest.raises(ValidationError, match="model_name"):
        _make_llm(model_name=None)


def test_model_name_empty_raises():
    with pytest.raises(ValidationError, match="model_name"):
        _make_llm(model_name="")


def test_model_name_whitespace_raises():
    with pytest.raises(ValidationError, match="model_name"):
        _make_llm(model_name="  ")


# ──────────────────────────────────────────────────────────────────────────────
# headers validation
# ──────────────────────────────────────────────────────────────────────────────
def test_headers_dict_wrapped_to_callable():
    llm = _make_llm(headers={"Authorization": "Bearer xxx"})
    assert callable(llm.headers)
    result = llm.headers(None)
    assert result == {"Authorization": "Bearer xxx"}


def test_headers_callable_stays_callable():
    fn = lambda req: {"X-Custom": "value"}
    llm = _make_llm(headers=fn)
    assert callable(llm.headers)
    assert llm.headers(None) == {"X-Custom": "value"}


def test_headers_invalid_type_raises():
    with pytest.raises(ValidationError, match="headers"):
        _make_llm(headers=42)


# ──────────────────────────────────────────────────────────────────────────────
# _execute raises NotImplementedError
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_execute_not_implemented():
    llm = _make_llm()
    with pytest.raises(NotImplementedError):
        await llm._execute(None)
