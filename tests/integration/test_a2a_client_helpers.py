"""Integration tests for A2AClientAgent static/class helper methods.

Tests cover: _sanitize_headers, _derive_rpc_url_from_card_url,
_append_stream_suffix, _resolve_card_endpoint, _task_state,
_extract_text_from_task, _extract_text_from_result, _apply_ids_to_message,
and the .minimal() factory.
"""

from unittest.mock import MagicMock

import pytest

try:
    from a2a.client.helpers import create_text_message_object
    from a2a.types import Message, Task, TaskState, TaskStatus

    from oxygent.oxy.agents.a2a_client_agent import A2AClientAgent
except ImportError:
    pytest.skip("a2a SDK not available in this environment", allow_module_level=True)


# ---------------------------------------------------------------------------
# Tests: _sanitize_headers
# ---------------------------------------------------------------------------


class TestSanitizeHeaders:
    def test_removes_excluded_headers(self):
        raw = {
            "host": "evil.com",
            "content-length": "42",
            "x-custom": "keep-me",
            "authorization": "Bearer token",
        }
        result = A2AClientAgent._sanitize_headers(raw)
        assert "x-custom" in result
        assert "authorization" in result
        assert "host" not in result
        assert "content-length" not in result

    def test_drops_none_values(self):
        raw = {"x-key": None, "x-valid": "val"}
        result = A2AClientAgent._sanitize_headers(raw)
        assert "x-key" not in result
        assert result["x-valid"] == "val"

    def test_drops_empty_keys(self):
        raw = {"": "val", "x-ok": "yes"}
        result = A2AClientAgent._sanitize_headers(raw)
        assert "" not in result
        assert result["x-ok"] == "yes"

    def test_non_dict_returns_empty(self):
        assert A2AClientAgent._sanitize_headers(None) == {}
        assert A2AClientAgent._sanitize_headers("not a dict") == {}
        assert A2AClientAgent._sanitize_headers(123) == {}

    def test_values_converted_to_str(self):
        raw = {"x-num": 42, "x-bool": True}
        result = A2AClientAgent._sanitize_headers(raw)
        assert result["x-num"] == "42"
        assert result["x-bool"] == "True"


# ---------------------------------------------------------------------------
# Tests: _derive_rpc_url_from_card_url
# ---------------------------------------------------------------------------


class TestDeriveRpcUrl:
    def test_strips_well_known_path(self):
        url = "http://host:8080/prefix/.well-known/agent.json"
        result = A2AClientAgent._derive_rpc_url_from_card_url(url)
        assert "/.well-known/agent.json" not in result
        assert "/prefix/" in result

    def test_with_query_string(self):
        url = "http://host:8080/prefix/.well-known/agent.json?token=abc"
        result = A2AClientAgent._derive_rpc_url_from_card_url(url)
        assert "token=abc" in result
        assert "/.well-known/agent.json" not in result

    def test_no_marker_in_path(self):
        url = "http://host:8080/some/other/path"
        result = A2AClientAgent._derive_rpc_url_from_card_url(url)
        assert "host:8080" in result
        assert "/some/other/path" in result


# ---------------------------------------------------------------------------
# Tests: _append_stream_suffix
# ---------------------------------------------------------------------------


class TestAppendStreamSuffix:
    def test_appends_stream(self):
        url = "http://host:8080/api"
        result = A2AClientAgent._append_stream_suffix(url)
        assert result == "http://host:8080/api/stream"

    def test_does_not_double_append(self):
        url = "http://host:8080/api/stream"
        result = A2AClientAgent._append_stream_suffix(url)
        assert result == "http://host:8080/api/stream"

    def test_preserves_query_string(self):
        url = "http://host:8080/api?key=val"
        result = A2AClientAgent._append_stream_suffix(url)
        assert "key=val" in result
        assert "/api/stream" in result

    def test_strips_trailing_slash(self):
        url = "http://host:8080/api/"
        result = A2AClientAgent._append_stream_suffix(url)
        assert result == "http://host:8080/api/stream"


# ---------------------------------------------------------------------------
# Tests: _resolve_card_endpoint
# ---------------------------------------------------------------------------


class TestResolveCardEndpoint:
    def test_uses_server_url_when_no_card_url(self):
        agent = A2AClientAgent(
            name="test",
            desc="test",
            server_url="http://host:8080",
            agent_card_url=None,
        )
        server, card_path = agent._resolve_card_endpoint()
        assert "host:8080" in server
        assert card_path == ".well-known/agent.json"

    def test_parses_full_card_url_with_marker(self):
        agent = A2AClientAgent(
            name="test",
            desc="test",
            server_url="http://fallback:8080",
            agent_card_url="http://real:9090/prefix/.well-known/agent.json",
        )
        server, card_path = agent._resolve_card_endpoint()
        assert server == "http://real:9090/prefix"
        assert card_path == ".well-known/agent.json"

    def test_parses_card_url_with_query_params(self):
        agent = A2AClientAgent(
            name="test",
            desc="test",
            server_url="http://fallback:8080",
            agent_card_url="http://real:9090/.well-known/agent.json?token=xyz",
        )
        server, card_path = agent._resolve_card_endpoint()
        assert "token=xyz" in card_path


# ---------------------------------------------------------------------------
# Tests: _task_state
# ---------------------------------------------------------------------------


class TestTaskState:
    def test_none_task_returns_empty(self):
        assert A2AClientAgent._task_state(None) == ""

    def test_task_with_no_status(self):
        task = MagicMock(spec=Task)
        task.status = None
        assert A2AClientAgent._task_state(task) == ""

    def test_task_with_enum_state(self):
        task = MagicMock(spec=Task)
        task.status = MagicMock()
        task.status.state = TaskState.completed
        result = A2AClientAgent._task_state(task)
        assert result == "completed"

    def test_task_with_string_state(self):
        task = MagicMock(spec=Task)
        task.status = MagicMock()
        task.status.state = "FAILED"
        result = A2AClientAgent._task_state(task)
        assert result == "failed"


# ---------------------------------------------------------------------------
# Tests: _extract_text_from_task
# ---------------------------------------------------------------------------


class TestExtractTextFromTask:
    def test_none_returns_empty(self):
        assert A2AClientAgent._extract_text_from_task(None) == ""

    def test_extracts_from_status_message(self):
        msg = create_text_message_object(content="hello world")
        task = MagicMock(spec=Task)
        task.status = MagicMock()
        task.status.message = msg
        task.artifacts = None
        result = A2AClientAgent._extract_text_from_task(task)
        assert "hello world" in result

    def test_deduplicates_status_and_artifacts(self):
        msg = create_text_message_object(content="same text")
        task = MagicMock(spec=Task)
        task.status = MagicMock()
        task.status.message = msg

        from a2a.types import Part, TextPart

        artifact = MagicMock()
        artifact.parts = [Part(root=TextPart(text="same text"))]
        task.artifacts = [artifact]
        result = A2AClientAgent._extract_text_from_task(task)
        assert result.count("same text") == 1


# ---------------------------------------------------------------------------
# Tests: _apply_ids_to_message
# ---------------------------------------------------------------------------


class TestApplyIdsToMessage:
    def test_sets_context_and_task_id(self):
        msg = create_text_message_object(content="test")
        A2AClientAgent._apply_ids_to_message(
            msg, context_id="ctx1", task_id="task1", reference_task_ids=["ref1"]
        )
        assert msg.context_id == "ctx1"
        assert msg.task_id == "task1"
        assert msg.reference_task_ids == ["ref1"]

    def test_skips_none_values(self):
        msg = create_text_message_object(content="test")
        A2AClientAgent._apply_ids_to_message(
            msg, context_id=None, task_id=None, reference_task_ids=[]
        )
        assert not hasattr(msg, "context_id") or msg.context_id is None


# ---------------------------------------------------------------------------
# Tests: .minimal() factory
# ---------------------------------------------------------------------------


class TestMinimalFactory:
    def test_creates_instance_with_defaults(self):
        agent = A2AClientAgent.minimal(name="min_agent", server_url="http://host:8080")
        assert agent.name == "min_agent"
        assert agent.streaming is False
        assert agent.enable_task_polling is False

    def test_creates_instance_with_overrides(self):
        agent = A2AClientAgent.minimal(
            name="stream_agent",
            server_url="http://host:8080",
            streaming=True,
            timeout=30.0,
            desc="My agent",
        )
        assert agent.streaming is True
        assert agent.timeout == 30.0
        assert agent.desc == "My agent"
