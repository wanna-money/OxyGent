"""Unit tests for oxygent.oxy.agents.rag_agent (RAGAgent)."""

from unittest.mock import AsyncMock

import pytest

from oxygent.oxy.agents.rag_agent import RAGAgent
from oxygent.schemas import OxyRequest


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
        "oxygent.oxy.agents.local_agent.Config.get_agent_llm_model",
        lambda: "mock_llm",
        raising=True,
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_agent_prompt",
        lambda: "",
        raising=True,
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_vearch_config",
        lambda: {},
        raising=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────
def test_default_prompt_injected(patched_config):
    """Without explicit prompt, default RAG prompt is set."""

    async def dummy_retrieve(req):
        return "context"

    agent = RAGAgent(
        name="rag",
        func_retrieve_knowledge=dummy_retrieve,
    )
    assert "${knowledge}" in agent.prompt


def test_custom_prompt_preserved(patched_config):
    """Explicit prompt is not overwritten."""

    async def dummy_retrieve(req):
        return "context"

    agent = RAGAgent(
        name="rag",
        prompt="Custom prompt ${info}",
        func_retrieve_knowledge=dummy_retrieve,
    )
    assert agent.prompt == "Custom prompt ${info}"


def test_custom_placeholder(patched_config):
    """Custom knowledge_placeholder is used in default prompt."""

    async def dummy_retrieve(req):
        return "context"

    agent = RAGAgent(
        name="rag",
        knowledge_placeholder="context",
        func_retrieve_knowledge=dummy_retrieve,
    )
    assert "${context}" in agent.prompt


@pytest.mark.asyncio
async def test_pre_process_injects_knowledge(patched_config):
    """_pre_process calls retrieve function and injects knowledge."""

    async def mock_retrieve(req):
        return "retrieved knowledge"

    agent = RAGAgent(
        name="rag",
        func_retrieve_knowledge=mock_retrieve,
    )
    mas = DummyMAS()
    agent.set_mas(mas)

    req = OxyRequest(
        arguments={"query": "hello"},
        caller="user",
        caller_category="user",
    )
    req.mas = mas

    # monkeypatch the parent's _pre_process to just return the request
    original_pre_process = agent._pre_process

    result = await agent._pre_process(req)
    assert result.arguments["knowledge"] == "retrieved knowledge"
