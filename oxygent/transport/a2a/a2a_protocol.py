"""A2A protocol payload builders."""

from __future__ import annotations

from typing import Any

from ...utils.common_utils import generate_uuid


def rpc_ok(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    """Build JSON-RPC success envelope."""
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def rpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    """Build JSON-RPC error envelope."""
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message},
    }


def build_message_event(text: str, task_id: str, context_id: str) -> dict[str, Any]:
    """Build normalized A2A message event payload."""
    return {
        "kind": "message",
        "messageId": generate_uuid(),
        "role": "agent",
        "parts": [{"kind": "text", "text": text}],
        "taskId": task_id,
        "contextId": context_id,
    }


def build_agent_message(text: str, task_id: str, context_id: str) -> dict[str, Any]:
    """Build normalized agent message used in task status."""
    return {
        "kind": "message",
        "messageId": generate_uuid(),
        "role": "agent",
        "parts": [{"kind": "text", "text": text}],
        "taskId": task_id,
        "contextId": context_id,
    }


def build_final_artifact(text: str) -> dict[str, Any]:
    """Build a normalized text artifact for final answers."""
    return {
        "artifactId": generate_uuid(),
        "name": "final_answer",
        "parts": [{"kind": "text", "text": text}],
    }
