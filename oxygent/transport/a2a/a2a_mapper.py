"""A2A request/response mapping helpers.

Provides functions to normalize, extract, and translate between A2A protocol
payloads and OxyGent MAS internal chat payloads, including text extraction
from various A2A message shapes and SSE delta parsing.
"""

from __future__ import annotations

import json
from typing import Any

from ...utils.common_utils import generate_uuid


def normalize_message_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the message-level sub-dict for text/context extraction.

    Args:
        payload: Raw A2A request payload.

    Returns:
        The ``message`` sub-dictionary if present and valid, otherwise the
        original payload.
    """
    message = payload.get("message", {})
    return message if isinstance(message, dict) else payload


def extract_text(payload: dict[str, Any]) -> str:
    """Extract plain text from various A2A payload shapes.

    Checks ``query``, ``content``, ``text`` top-level keys, then walks the
    ``parts`` list looking for text parts. Falls back to JSON serialization
    of the entire payload when no text is found.

    Args:
        payload: Normalized A2A message payload.

    Returns:
        Extracted text string.
    """
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
    """Extract the metadata dictionary from a payload, defaulting to empty.

    Args:
        payload: Raw A2A request payload.

    Returns:
        Metadata dictionary, or empty dict if absent or invalid.
    """
    md = payload.get("metadata", {})
    return md if isinstance(md, dict) else {}


def extract_context_and_task(
    payload: dict[str, Any], fallback_message: dict[str, Any] | None = None
) -> tuple[str, str]:
    """Extract ``contextId`` and ``taskId``, generating UUIDs as fallback.

    Searches both the top-level payload and an optional fallback message dict
    for context and task identifiers in both camelCase and snake_case forms.

    Args:
        payload: Raw A2A request payload.
        fallback_message: Optional normalized message dict to search as well.

    Returns:
        Tuple of (context_id, task_id) strings.
    """
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
    """Extract the optional ``referenceTaskIds`` list from the payload.

    Args:
        payload: Raw A2A request payload.
        fallback_message: Optional normalized message dict to search.

    Returns:
        List of reference task ID strings (may be empty).
    """
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
    """Translate A2A request attributes into an OxyGent MAS chat payload.

    Builds the dict consumed by ``MAS.chat_with_agent()``, resolving
    ``from_trace_id`` from reference task IDs or prior session context.

    Args:
        text: User query text.
        context_id: A2A context identifier (maps to MAS group_id).
        task_id: A2A task identifier (maps to MAS current_trace_id).
        target: Target MAS agent name.
        reference_task_ids: Optional list of prior task IDs for conversation
            continuity.
        metadata: Optional A2A metadata to attach as group_data.
        context_session: Prior session state for this context (from store).

    Returns:
        MAS-compatible payload dictionary, or None if ``target`` is empty.
    """
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
    """Extract the text delta from an OxyGent SSE stream payload.

    Handles both raw string data and parsed JSON dicts. For JSON payloads
    with ``type=stream``, extracts ``content.delta``; for ``stream_end``,
    returns empty string.

    Args:
        data: SSE data field value -- either a raw string or parsed dict.
        parse_delta: If True (default), attempt to parse JSON and extract
            the delta. If False, return the raw/serialized value.

    Returns:
        Extracted text delta string (may be empty).
    """
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
