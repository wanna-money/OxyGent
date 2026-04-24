"""A minimal A2A client agent for OxyGent.

  This module provides a lightweight A2A client adapter with a small,
  stable configuration surface for common request/response and streaming
  scenarios.
"""

import asyncio
import json
import logging
import time
from typing import Any
from urllib.parse import parse_qs, urlsplit, urlunsplit
from uuid import uuid4

import httpx
from pydantic import Field, PrivateAttr

from ...schemas import OxyRequest, OxyResponse, OxyState
from .remote_agent import RemoteAgent

from a2a.client import A2AClient as A2ASDKClient, A2ACardResolver
from a2a.client.helpers import create_text_message_object
from a2a.types import (
    CancelTaskRequest,
    GetTaskRequest,
    Message,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
    Task,
    TaskArtifactUpdateEvent,
    TaskIdParams,
    TaskQueryParams,
    TaskResubscriptionRequest,
    TaskStatusUpdateEvent,
)
from a2a.utils.message import get_message_text
from a2a.utils.parts import get_text_parts

logger = logging.getLogger(__name__)

EXCLUDED_HEADERS = {
    "host",
    "connection",
    "sec-ch-ua",
    "sec-ch-ua-mobile",
    "sec-ch-ua-platform",
    "user-agent",
    "referer",
    "accept-encoding",
    "accept-language",
    "cache-control",
    "sec-fetch-site",
    "sec-fetch-mode",
    "sec-fetch-dest",
    "accept",
    "content-length",
}


class A2AClientAgent(RemoteAgent):
    """Remote agent adapter for A2A-compatible servers.

    Responsibilities:
    - Resolve and validate agent card from `server_url` or `agent_card_url`.
    - Send messages through the A2A legacy client (`message/send` or `message/stream`).
    - Normalize A2A responses into `OxyResponse` and persist `context_id`/`task_id`
      in OxyGent shared session data.

    Notes:
    - This implementation intentionally targets the legacy A2A SDK client path.
    - Streaming output is printed to stdout by design to keep demo/CLI behavior.
    """

    agent_card_url: str | None = Field(
        None,
        description=(
            "Optional full card URL, e.g. "
            "http://host/.../.well-known/agent.json?token=..."
        ),
    )
    card_path: str | None = Field(
        ".well-known/agent.json", description="Relative card path when using server_url."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Default A2A metadata."
    )
    headers: dict[str, str] = Field(
        default_factory=dict, description="Static HTTP headers for A2A calls."
    )
    streaming: bool = Field(False, description="Use streaming request mode.")
    append_stream_suffix_to_url: bool = Field(
        False,
        description="Whether to append '/stream' to card.url when streaming=True.",
    )
    enable_task_polling: bool = Field(
        True, description="Whether to poll tasks/get for task final state."
    )
    task_poll_interval_seconds: float = Field(3.0)
    task_poll_max_wait_seconds: float = Field(60.0)
    task_terminal_states: list[str] = Field(
        default_factory=lambda: ["completed", "failed", "canceled", "rejected"]
    )

    _client: Any = PrivateAttr(default=None)
    _card: Any = PrivateAttr(default=None)
    _http_client: httpx.AsyncClient | None = PrivateAttr(default=None)

    @classmethod
    def minimal(
        cls,
        *,
        name: str,
        server_url: str,
        agent_card_url: str | None = None,
        card_url: str | None = None,
        metadata: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        streaming: bool = False,
        append_stream_suffix_to_url: bool = False,
        timeout: float = 120.0,
        enable_task_polling: bool = False,
        task_poll_interval_seconds: float = 3.0,
        task_poll_max_wait_seconds: float = 10.0,
        desc: str = "",
    ) -> "A2AClientAgent":
        return cls(
            name=name,
            desc=desc,
            server_url=server_url,
            agent_card_url=agent_card_url or card_url,
            metadata=metadata or {},
            headers=headers or {},
            streaming=streaming,
            append_stream_suffix_to_url=append_stream_suffix_to_url,
            timeout=timeout,
            enable_task_polling=enable_task_polling,
            task_poll_interval_seconds=task_poll_interval_seconds,
            task_poll_max_wait_seconds=task_poll_max_wait_seconds,
        )

    @staticmethod
    def _sanitize_headers(raw_headers: dict[str, Any] | None) -> dict[str, str]:
        """Drop unsafe headers and normalize values to strings."""
        if not isinstance(raw_headers, dict):
            return {}
        return {
            str(k): str(v)
            for k, v in raw_headers.items()
            if k and v is not None and str(k).lower() not in EXCLUDED_HEADERS
        }

    @staticmethod
    def _derive_rpc_url_from_card_url(card_url: str) -> str:
        parsed = urlsplit(card_url)
        marker = "/.well-known/agent.json"
        path = parsed.path
        if marker in path:
            path = path.split(marker, 1)[0] + "/"
        return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))

    @staticmethod
    def _append_stream_suffix(url: str) -> str:
        """Append '/stream' to URL path while preserving query string."""
        parsed = urlsplit(url)
        path = parsed.path.rstrip("/")
        if not path.endswith("/stream"):
            path = f"{path}/stream"
        return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))

    def _resolve_card_endpoint(self) -> tuple[str, str]:
        """Resolve card endpoint from either server_url or full card URL."""
        if not self.agent_card_url:
            return str(self.server_url), self.card_path or ".well-known/agent.json"

        parsed = urlsplit(self.agent_card_url)
        marker = "/.well-known/agent.json"
        path = parsed.path
        if marker in path:
            base_path, _ = path.split(marker, 1)
            server_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"
            card_path = ".well-known/agent.json"
        else:
            server_url = f"{parsed.scheme}://{parsed.netloc}"
            card_path = parsed.path or (self.card_path or ".well-known/agent.json")

        query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        if query_params:
            query_str = "&".join(f"{k}={v}" for k, v in query_params.items())
            card_path = f"{card_path}?{query_str}"
        return server_url, card_path

    async def init(self):
        """Initialize A2A card resolver and SDK client."""
        await super().init()
        server_url, card_path = self._resolve_card_endpoint()
        logger.debug(
            "Initializing A2AClientAgent agent=%s server_url=%s streaming=%s polling=%s",
            self.name,
            server_url,
            self.streaming,
            self.enable_task_polling,
            extra={
                "agent": self.name,
                "server_url": server_url,
                "streaming": self.streaming,
                "polling": self.enable_task_polling,
            },
        )

        static_headers = self._sanitize_headers(self.headers)
        self._http_client = httpx.AsyncClient(
            headers=static_headers or None, timeout=self.timeout
        )
        resolver = A2ACardResolver(
            httpx_client=self._http_client,
            base_url=server_url,
            agent_card_path=card_path,
        )
        card = await resolver.get_agent_card()

        if self.agent_card_url:
            card.url = self._derive_rpc_url_from_card_url(self.agent_card_url)
        if (
            self.streaming
            and self.append_stream_suffix_to_url
            and getattr(card, "url", None)
        ):
            card.url = self._append_stream_suffix(card.url)

        self._card = card
        self._client = A2ASDKClient(httpx_client=self._http_client, agent_card=card)

        self.org = {
            "children": [
                {
                    "name": self.name,
                    "type": "agent",
                    "desc": self.desc or (self._card.description or self.name),
                    "children": [],
                }
            ]
        }
        if not self.desc:
            self.desc = self._card.description or ""
        self._set_desc_for_llm()

        logger.debug(
            "A2AClientAgent initialized agent=%s card_url=%s",
            self.name,
            getattr(self._card, "url", ""),
            extra={"agent": self.name, "card_url": getattr(self._card, "url", "")},
        )

    @staticmethod
    def _task_state(task: Task | None) -> str:
        if not task or not task.status:
            return ""
        state = task.status.state
        return str(getattr(state, "value", state)).lower()

    @staticmethod
    def _extract_text_from_task(task: Task | None) -> str:
        if not task:
            return ""
        chunks: list[str] = []
        if task.status and task.status.message:
            text = get_message_text(task.status.message)
            if text:
                chunks.append(text)
        if task.artifacts:
            for artifact in task.artifacts:
                chunks.extend(get_text_parts(artifact.parts or []))
        # Many A2A servers return the same final text in both status.message
        # and artifacts. Deduplicate while preserving order.
        deduped: list[str] = []
        seen: set[str] = set()
        for chunk in chunks:
            text = (chunk or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            deduped.append(text)
        return "\n".join(deduped).strip()

    @staticmethod
    def _extract_text_from_result(result: Any) -> str:
        if isinstance(result, Message):
            return get_message_text(result) or ""
        if isinstance(result, Task):
            return A2AClientAgent._extract_text_from_task(result)
        if isinstance(result, str):
            return result
        return ""

    def _build_metadata(self, oxy_request: OxyRequest) -> dict[str, Any]:
        """Merge default metadata with per-request metadata."""
        merged = dict(self.metadata)
        runtime_metadata = oxy_request.arguments.get("metadata", {})
        if isinstance(runtime_metadata, dict):
            merged.update(runtime_metadata)
        return merged

    def _build_http_kwargs(self, oxy_request: OxyRequest) -> dict[str, Any] | None:
        """Build per-request http kwargs with safe inherited headers."""
        raw_headers = oxy_request.get_shared_data("_headers", {})
        inherited = self._sanitize_headers(raw_headers)
        if not inherited:
            return None
        return {"headers": inherited}

    def _load_session_ids(
        self, oxy_request: OxyRequest
    ) -> tuple[str | None, str | None, list[str], str]:
        """Load context/task/reference ids from request and shared session."""
        shared_key = f"_session_{self.name}"
        shared = oxy_request.shared_data.get(shared_key, {})

        context_id = oxy_request.arguments.get("context_id") or shared.get("context_id")
        task_id = oxy_request.arguments.get("task_id") or shared.get("task_id")
        reference_task_ids = (
            oxy_request.arguments.get("reference_task_ids")
            or oxy_request.arguments.get("referenceTaskIds")
            or []
        )
        if not isinstance(reference_task_ids, list):
            reference_task_ids = []

        return context_id, task_id, reference_task_ids, shared_key

    @staticmethod
    def _apply_ids_to_message(
        message: Message,
        *,
        context_id: str | None,
        task_id: str | None,
        reference_task_ids: list[str],
    ) -> None:
        """Apply A2A ids onto outgoing message object."""
        if context_id:
            message.context_id = context_id
        if task_id:
            message.task_id = task_id
        if reference_task_ids:
            message.reference_task_ids = [str(x) for x in reference_task_ids if x]

    async def _send_non_stream(
        self,
        *,
        message: Message,
        metadata: dict[str, Any],
        context_id: str | None,
        task_id: str | None,
        http_kwargs: dict[str, Any] | None = None,
    ) -> tuple[str, str | None, str | None, list[str]]:
        """Execute `message/send` once and extract text result."""
        req = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message=message, metadata=metadata or None),
        )
        resp = await self._client.send_message(req, http_kwargs=http_kwargs)
        result = getattr(resp.root, "result", None)

        if isinstance(result, Message):
            context_id = getattr(result, "context_id", context_id)
            task_id = getattr(result, "task_id", task_id)
        elif isinstance(result, Task):
            context_id = getattr(result, "context_id", context_id)
            task_id = getattr(result, "id", task_id)

        answer = self._extract_text_from_result(result)
        return answer, context_id, task_id, []

    async def _send_stream(
        self,
        *,
        message: Message,
        metadata: dict[str, Any],
        context_id: str | None,
        task_id: str | None,
        http_kwargs: dict[str, Any] | None = None,
    ) -> tuple[str, str | None, str | None, list[str]]:
        """Execute `message/stream`, print deltas, and accumulate final text."""
        req = SendStreamingMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message=message, metadata=metadata or None),
        )

        emitted = ""
        stream_deltas: list[str] = []

        async for chunk in self._client.send_message_streaming(
            req, http_kwargs=http_kwargs
        ):
            root = getattr(chunk, "root", None)
            if root is None:
                continue

            if hasattr(root, "error") and getattr(root, "error", None) is not None:
                err = getattr(root, "error")
                err_msg = getattr(err, "message", None) or str(err)
                raise RuntimeError(f"A2A streaming error: {err_msg}")

            result = getattr(root, "result", None)
            text = ""
            if isinstance(result, Message):
                context_id = getattr(result, "context_id", context_id)
                task_id = getattr(result, "task_id", task_id)
                text = self._extract_text_from_result(result)
            elif isinstance(result, Task):
                context_id = getattr(result, "context_id", context_id)
                task_id = getattr(result, "id", task_id)
                text = self._extract_text_from_result(result)
            elif isinstance(result, TaskStatusUpdateEvent):
                context_id = getattr(result, "context_id", context_id)
                task_id = getattr(result, "task_id", task_id)
                status = getattr(result, "status", None)
                status_message = getattr(status, "message", None) if status else None
                text = get_message_text(status_message) if status_message else ""
            elif isinstance(result, TaskArtifactUpdateEvent):
                context_id = getattr(result, "context_id", context_id)
                task_id = getattr(result, "task_id", task_id)
                artifact = getattr(result, "artifact", None)
                text = "\n".join(
                    get_text_parts(getattr(artifact, "parts", None) or [])
                ).strip()

            if not text:
                continue

            delta = text[len(emitted) :] if text.startswith(emitted) else text
            emitted = text if text.startswith(emitted) else (emitted + text)
            if delta:
                stream_deltas.append(delta)
                # Keep stdout behavior for demos and CLI-style runs.
                print(delta, end="", flush=True)

        return emitted, context_id, task_id, stream_deltas

    async def _poll_task_if_needed(
        self,
        *,
        task_id: str | None,
        metadata: dict[str, Any],
        answer: str,
        context_id: str | None,
        http_kwargs: dict[str, Any] | None = None,
    ) -> tuple[str, str | None, dict[str, Any], Task | None]:
        """Poll tasks/get until terminal state or timeout."""
        if not (self.enable_task_polling and task_id):
            return answer, context_id, {}, None

        start = time.time()
        rounds = 0
        terminal = {x.lower() for x in self.task_terminal_states}
        final_task = None
        poll_info = {}

        while True:
            rounds += 1
            try:
                final_task = await self._get_task(
                    task_id, metadata=metadata or None, http_kwargs=http_kwargs
                )
            except Exception as e:
                poll_info = {
                    "poll_rounds": rounds,
                    "poll_state": "poll_error",
                    "poll_wait_seconds": round(time.time() - start, 3),
                    "poll_error": str(e),
                }
                logger.warning(
                    "Task polling failed agent=%s task_id=%s error=%s",
                    self.name,
                    task_id,
                    e,
                )
                break
            if final_task:
                context_id = getattr(final_task, "context_id", context_id)
                text = self._extract_text_from_task(final_task)
                if text:
                    answer = text
                state = self._task_state(final_task)
            else:
                state = ""

            if state in terminal:
                poll_info = {
                    "poll_rounds": rounds,
                    "poll_state": state,
                    "poll_wait_seconds": round(time.time() - start, 3),
                }
                break

            if (time.time() - start) >= self.task_poll_max_wait_seconds:
                poll_info = {
                    "poll_rounds": rounds,
                    "poll_state": state or "timeout",
                    "poll_wait_seconds": round(time.time() - start, 3),
                }
                break

            await asyncio.sleep(self.task_poll_interval_seconds)

        logger.debug(
            "Task polling finished agent=%s task_id=%s polling=%s",
            self.name,
            task_id,
            poll_info,
            extra={"agent": self.name, "task_id": task_id, "polling": poll_info},
        )
        return answer, context_id, poll_info, final_task

    async def _get_task(
        self,
        task_id: str,
        metadata: dict[str, Any] | None = None,
        http_kwargs: dict[str, Any] | None = None,
    ) -> Task | None:
        request = GetTaskRequest(
            id=str(uuid4()),
            params=TaskQueryParams(id=task_id, metadata=metadata or None),
        )
        response = await self._client.get_task(request, http_kwargs=http_kwargs)
        return getattr(response.root, "result", None)

    async def get_task(
        self,
        task_id: str,
        metadata: dict[str, Any] | None = None,
        oxy_request: OxyRequest | None = None,
    ) -> dict[str, Any]:
        http_kwargs = (
            self._build_http_kwargs(oxy_request) if oxy_request is not None else None
        )
        task = await self._get_task(task_id, metadata=metadata, http_kwargs=http_kwargs)
        return (
            task.model_dump(mode="json", by_alias=True, exclude_none=True) if task else {}
        )

    async def cancel_task(
        self, task_id: str, oxy_request: OxyRequest | None = None
    ) -> dict[str, Any]:
        request = CancelTaskRequest(id=str(uuid4()), params=TaskIdParams(id=task_id))
        http_kwargs = (
            self._build_http_kwargs(oxy_request) if oxy_request is not None else None
        )
        response = await self._client.cancel_task(request, http_kwargs=http_kwargs)
        result = getattr(response.root, "result", None)
        return (
            result.model_dump(mode="json", by_alias=True, exclude_none=True)
            if result
            else {}
        )

    async def resubscribe(
        self, task_id: str, oxy_request: OxyRequest | None = None
    ) -> list[dict[str, Any]]:
        request = TaskResubscriptionRequest(
            id=str(uuid4()), params=TaskIdParams(id=task_id)
        )
        http_kwargs = (
            self._build_http_kwargs(oxy_request) if oxy_request is not None else None
        )
        events = []
        async for event in self._client.resubscribe(request, http_kwargs=http_kwargs):
            result = getattr(event.root, "result", None)
            if hasattr(result, "model_dump"):
                events.append(
                    result.model_dump(mode="json", by_alias=True, exclude_none=True)
                )
        return events

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Send request to A2A server and normalize response as OxyResponse."""
        query = oxy_request.get_query() or json.dumps(
            oxy_request.arguments, ensure_ascii=False
        )

        message = create_text_message_object(content=query)
        merged_metadata = self._build_metadata(oxy_request)
        http_kwargs = self._build_http_kwargs(oxy_request)
        if merged_metadata:
            message.metadata = merged_metadata

        context_id, task_id, reference_task_ids, shared_key = self._load_session_ids(
            oxy_request
        )
        self._apply_ids_to_message(
            message,
            context_id=context_id,
            task_id=task_id,
            reference_task_ids=reference_task_ids,
        )

        logger.debug(
            "A2A execute start agent=%s streaming=%s context_id=%s task_id=%s has_references=%s",
            self.name,
            self.streaming,
            context_id,
            task_id,
            bool(reference_task_ids),
            extra={
                "agent": self.name,
                "streaming": self.streaming,
                "context_id": context_id,
                "task_id": task_id,
                "has_references": bool(reference_task_ids),
            },
        )

        if self.streaming:
            answer, context_id, task_id, stream_deltas = await self._send_stream(
                message=message,
                metadata=merged_metadata,
                context_id=context_id,
                task_id=task_id,
                http_kwargs=http_kwargs,
            )
        else:
            answer, context_id, task_id, stream_deltas = await self._send_non_stream(
                message=message,
                metadata=merged_metadata,
                context_id=context_id,
                task_id=task_id,
                http_kwargs=http_kwargs,
            )

        answer, context_id, poll_info, final_task = await self._poll_task_if_needed(
            task_id=task_id,
            metadata=merged_metadata,
            answer=answer,
            context_id=context_id,
            http_kwargs=http_kwargs,
        )

        oxy_request.shared_data[shared_key] = {
            "context_id": context_id,
            "task_id": task_id,
        }

        logger.debug(
            "A2A execute finish agent=%s context_id=%s task_id=%s output_len=%s",
            self.name,
            context_id,
            task_id,
            len((answer or "").strip()),
            extra={
                "agent": self.name,
                "context_id": context_id,
                "task_id": task_id,
                "output_len": len((answer or "").strip()),
            },
        )

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=(answer or "").strip(),
            extra={
                "context_id": context_id,
                "task_id": task_id,
                "polling": poll_info,
                "stream_deltas": stream_deltas,
                "final_task": final_task.model_dump(
                    mode="json", by_alias=True, exclude_none=True
                )
                if final_task
                else None,
            },
        )
