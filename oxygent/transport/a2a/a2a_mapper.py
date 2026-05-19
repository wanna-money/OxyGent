"""A2A request/response mapping helpers."""

from __future__ import annotations

import json
from typing import Any

from ...utils.common_utils import generate_uuid


def normalize_message_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return normalized message-level payload for text/context extraction."""
    message = payload.get("message", {})
    return message if isinstance(message, dict) else payload


def extract_text(payload: dict[str, Any]) -> str:
    """Extract plain text from common A2A payload shapes."""
    if not isinstance(payload, dict):
        return str(payload)

    for key in ("query", "content", "text"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value

    parts = payload.get("parts", [])
    if isinstance(parts, list):
        for part in parts:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                return text
            part_obj = part.get("part", {})
            if (
                isinstance(part_obj, dict)
                and part_obj.get("kind") == "text"
                and isinstance(part_obj.get("text"), str)
            ):
                return part_obj["text"]

    message = payload.get("message", {})
    if isinstance(message, dict):
        message_parts = message.get("parts", [])
        if isinstance(message_parts, list):
            for part in message_parts:
                if (
                    isinstance(part, dict)
                    and part.get("kind") == "text"
                    and isinstance(part.get("text"), str)
                ):
                    return part["text"]

    return json.dumps(payload, ensure_ascii=False)


def extract_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract metadata object safely from payload."""
    md = payload.get("metadata", {})
    return md if isinstance(md, dict) else {}


def extract_context_and_task(
    payload: dict[str, Any], fallback_message: dict[str, Any] | None = None
) -> tuple[str, str]:
    """Extract ``contextId`` and ``taskId`` with fallback generation."""
    msg = fallback_message or {}
    task_id = (
        payload.get("taskId")
        or payload.get("task_id")
        or msg.get("taskId")
        or msg.get("task_id")
        or generate_uuid()
    )
    context_id = (
        payload.get("contextId")
        or payload.get("context_id")
        or msg.get("contextId")
        or msg.get("context_id")
        or generate_uuid()
    )
    return str(context_id), str(task_id)


def extract_reference_task_ids(
    payload: dict[str, Any], fallback_message: dict[str, Any] | None = None
) -> list[str]:
    """Extract optional ``referenceTaskIds`` from payload/message."""
    msg = fallback_message or {}
    refs = (
        payload.get("referenceTaskIds")
        or payload.get("reference_task_ids")
        or msg.get("referenceTaskIds")
        or msg.get("reference_task_ids")
        or []
    )
    if not isinstance(refs, list):
        return []
    return [str(x) for x in refs if x]


def build_mas_payload(
    *,
    text: str,
    context_id: str,
    task_id: str,
    target: str,
    reference_task_ids: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    context_session: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Translate A2A request attributes into MAS chat payload."""
    if not target:
        return None

    payload: dict[str, Any] = {
        "query": text,
        "callee": target,
        "group_id": context_id,
        "current_trace_id": task_id,
        "from_trace_id": "",
    }
    session = context_session or {}
    ref_last = (reference_task_ids or [])[-1] if reference_task_ids else ""
    if ref_last and ref_last != task_id:
        payload["from_trace_id"] = ref_last
    elif session.get("last_trace_id") and session["last_trace_id"] != task_id:
        payload["from_trace_id"] = session["last_trace_id"]

    if metadata:
        payload["group_data"] = {"a2a_metadata": metadata}
    return payload


def extract_delta_from_sse_data(data: Any, parse_delta: bool = True) -> str:
    """Extract text delta from OxyGent SSE payload shapes."""
    parsed_data = data
    if isinstance(data, str):
        if not parse_delta:
            return data
        try:
            parsed_data = json.loads(data)
        except Exception:
            # Non-JSON string data is valid SSE content; return as-is
            return data

    if not isinstance(parsed_data, dict):
        return str(parsed_data or "")

    if not parse_delta:
        return json.dumps(parsed_data, ensure_ascii=False)

    msg_type = parsed_data.get("type", "")
    if msg_type == "stream":
        return str(parsed_data.get("content", {}).get("delta", "") or "")
    if msg_type in ("stream_end",):
        return ""

    content = parsed_data.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        output = content.get("output")
        if isinstance(output, str):
            return output
    return ""
