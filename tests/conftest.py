"""Shared pytest fixtures for integration, e2e, and regression tests.

Provides reusable factories for MockLLM, FunctionTool, MAS, and OxyRequest
so that test files don't each need to define their own DummyMAS boilerplate.
"""

import asyncio
import copy
import json
from typing import Any, Callable, Optional
from unittest.mock import AsyncMock

import pytest

from oxygent.config import Config
from oxygent.oxy.function_tools.function_tool import FunctionTool
from oxygent.oxy.llms.mock_llm import MockLLM
from oxygent.schemas import OxyRequest

# ---------------------------------------------------------------------------
# Config isolation
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_config():
    """Save and restore Config class state between tests."""
    orig_config = copy.deepcopy(Config._config)
    orig_env = Config._env
    yield
    Config._config = orig_config
    Config._env = orig_env


@pytest.fixture(autouse=True)
def patch_config_defaults(monkeypatch):
    """Patch Config defaults to avoid loading config.json and to use MemoryEs."""
    monkeypatch.setattr(
        "oxygent.config.Config.get_storage_es_engine", lambda: "MemoryEs"
    )
    monkeypatch.setattr("oxygent.config.Config.get_es_config", lambda: None)
    monkeypatch.setattr("oxygent.config.Config.get_redis_config", lambda: None)
    monkeypatch.setattr("oxygent.config.Config.get_vearch_config", lambda: None)
    monkeypatch.setattr(
        "oxygent.config.Config.get_live_prompt_is_active", lambda: False
    )


# ---------------------------------------------------------------------------
# DummyMAS (lightweight alternative for tests that don't need full MAS init)
# ---------------------------------------------------------------------------


async def _identity_process_message(msg, req):
    return msg


class DummyMAS:
    """Lightweight MAS stand-in for tests that only need oxy_name_to_oxy."""

    def __init__(self):
        self.oxy_name_to_oxy: dict[str, Any] = {}
        self.es_client = AsyncMock()
        self.vearch_client = None
        self.redis_client = None
        self.background_tasks: dict[str, set] = {}
        self.message_prefix = "test"
        self.name = "test_mas"
        self.global_data: dict[str, Any] = {}
        self.func_process_message = _identity_process_message
        self.active_tasks: dict[str, asyncio.Task] = {}
        self.event_dict: dict[str, asyncio.Event] = {}
        self.stream_dict: dict[str, list] = {}
        self.feedback_dict: dict[str, asyncio.Queue] = {}
        self.channel_id_dict: dict[str, list] = {}

    def add_oxy(self, oxy):
        self.oxy_name_to_oxy[oxy.name] = oxy

    def add_background_task(self, trace_id, task):
        self.background_tasks.setdefault(trace_id, set()).add(task)
        task.add_done_callback(
            lambda t: self.background_tasks.get(trace_id, set()).discard(t)
        )

    def is_agent(self, oxy_name: str) -> bool:
        from oxygent.oxy.agents.base_agent import BaseAgent
        from oxygent.oxy.base_flow import BaseFlow

        oxy = self.oxy_name_to_oxy.get(oxy_name)
        if oxy is None:
            return False
        return isinstance(oxy, (BaseFlow, BaseAgent))

    async def send_message(self, message, redis_key, group_id=""):
        pass


@pytest.fixture
def dummy_mas():
    return DummyMAS()


# ---------------------------------------------------------------------------
# MockLLM factory
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_llm_factory():
    """Factory that creates MockLLM instances with custom response functions."""

    def _create(
        name: str = "default_llm",
        response: str = "mock response",
        func: Optional[Callable] = None,
    ) -> MockLLM:
        if func is None:

            async def _static_response(oxy_request: OxyRequest) -> str:
                return response

            func = _static_response

        return MockLLM(name=name, func_mock_process=func)

    return _create


# ---------------------------------------------------------------------------
# FunctionTool factory
# ---------------------------------------------------------------------------


@pytest.fixture
def function_tool_factory():
    """Factory that creates FunctionTool instances wrapping Python functions."""

    def _create(
        name: str = "test_tool",
        desc: str = "A test tool",
        func: Optional[Callable] = None,
    ) -> FunctionTool:
        if func is None:

            async def _default_func() -> str:
                return f"{name}_result"

            func = _default_func

        return FunctionTool(name=name, desc=desc, func_process=func)

    return _create


# ---------------------------------------------------------------------------
# OxyRequest factory
# ---------------------------------------------------------------------------


@pytest.fixture
def oxy_request_factory():
    """Factory that creates OxyRequest instances with standard defaults."""

    def _create(
        query: str = "test query",
        caller: str = "user",
        caller_category: str = "user",
        mas: Any = None,
        **kwargs,
    ) -> OxyRequest:
        req = OxyRequest(
            arguments={"query": query},
            caller=caller,
            caller_category=caller_category,
            **kwargs,
        )
        if mas is not None:
            req.set_mas(mas)
        return req

    return _create


# ---------------------------------------------------------------------------
# Helper: build a simple ReAct LLM mock that responds with tool calls then answers
# ---------------------------------------------------------------------------


def make_react_llm_func(tool_calls: list[dict], final_answer: str):
    """Create a MockLLM function that first produces tool_call JSON responses,
    then produces a plain text answer.

    Args:
        tool_calls: List of dicts like {"tool_name": "...", "arguments": {...}}
        final_answer: The final answer text to return after all tool calls.
    """
    call_count = 0

    async def _react_llm(oxy_request: OxyRequest) -> str:
        nonlocal call_count
        messages = oxy_request.arguments.get("messages", [])
        has_observation = any(
            "execution result" in str(m.get("content", "")).lower()
            for m in messages
            if isinstance(m, dict)
        )
        if call_count < len(tool_calls) and not has_observation:
            result = json.dumps(tool_calls[call_count])
            call_count += 1
            return result
        if has_observation:
            call_count += 1
            return final_answer
        return final_answer

    return _react_llm


def make_sequential_llm_func(responses: list[str]):
    """Create a MockLLM function that returns responses in order."""
    idx = 0

    async def _sequential_llm(oxy_request: OxyRequest) -> str:
        nonlocal idx
        if idx < len(responses):
            result = responses[idx]
            idx += 1
            return result
        return responses[-1]

    return _sequential_llm
