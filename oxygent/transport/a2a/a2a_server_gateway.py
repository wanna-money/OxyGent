"""A2A server gateway for OxyGent MAS."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any

from a2a.types import TaskState
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from .a2a_card import build_agent_card, effective_target
from .a2a_mapper import (
    build_mas_payload,
    extract_context_and_task,
    extract_delta_from_sse_data,
    extract_metadata,
    extract_reference_task_ids,
    extract_text,
    normalize_message_payload,
)
from .a2a_protocol import build_message_event, rpc_error, rpc_ok
from .a2a_store import A2AInMemoryStore

logger = logging.getLogger(__name__)


class A2AServerGateway(BaseModel):
    """Protocol gateway that serves A2A endpoints for OxyGent."""

    mas: Any = Field(None, exclude=True, repr=False)
    target_agent_name: str = Field(
        "master_agent",
        description=(
            "Resolved target agent name. It is synchronized from MAS master_agent_name "
            "after set_mas()."
        ),
    )
    a2a_base_path: str = Field(
        "/a2a", description="Base path where A2A endpoints are mounted."
    )
    agent_version: str = Field("0.1.0", description="Server agent version.")
    capabilities: dict[str, Any] = Field(
        default_factory=lambda: {
            "streaming": True,
            "task_control": True,
            "stateTransitionHistory": True,
            "pushNotifications": False,
        },
        description="A2A capability declaration.",
    )
    parse_stream_delta: bool = Field(
        True,
        description=(
            "Whether to parse OxyGent SSE stream payload and extract content.delta. "
            "If False, keep raw stream payload text."
        ),
    )
    stream_task_update_char_interval: int = Field(
        128,
        description=(
            "Minimum emitted character delta before refreshing in-memory task snapshot "
            "during streaming."
        ),
    )
    stream_task_update_time_interval_seconds: float = Field(
        1.0,
        description=(
            "Maximum interval in seconds between in-memory task snapshot refreshes "
            "during streaming."
        ),
    )
    skills: list[dict[str, Any]] = Field(
        default_factory=list, description="Optional static skills override."
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _store: A2AInMemoryStore = PrivateAttr(default_factory=A2AInMemoryStore)

    def set_mas(self, mas: Any) -> None:
        """Bind MAS runtime and sync default target to master agent."""
        self.mas = mas
        master_name = getattr(mas, "master_agent_name", "") if mas else ""
        self.target_agent_name = master_name or "master_agent"
        logger.info(
            "A2AServerGateway bound to MAS",
            extra={
                "target_agent_name": self.target_agent_name,
                "a2a_base_path": self.a2a_base_path,
            },
        )

    # Thin wrappers retained for backward compatibility with previous method names.
    @staticmethod
    def _normalize_message_payload(payload: dict[str, Any]) -> dict[str, Any]:
        return normalize_message_payload(payload)

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        return extract_text(payload)

    @staticmethod
    def _extract_metadata(payload: dict[str, Any]) -> dict[str, Any]:
        return extract_metadata(payload)

    @staticmethod
    def _extract_context_and_task(
        payload: dict[str, Any], fallback_message: dict[str, Any] | None = None
    ) -> tuple[str, str]:
        return extract_context_and_task(payload, fallback_message)

    @staticmethod
    def _extract_reference_task_ids(
        payload: dict[str, Any], fallback_message: dict[str, Any] | None = None
    ) -> list[str]:
        return extract_reference_task_ids(payload, fallback_message)

    @staticmethod
    def _extract_delta_from_sse_data(data: Any, parse_delta: bool = True) -> str:
        return extract_delta_from_sse_data(data, parse_delta=parse_delta)

    @staticmethod
    def _rpc_ok(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return rpc_ok(req_id, result)

    @staticmethod
    def _rpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
        return rpc_error(req_id, code, message)

    @staticmethod
    def _build_message_event(
        text: str, task_id: str, context_id: str
    ) -> dict[str, Any]:
        return build_message_event(text, task_id, context_id)

    def _effective_target(self) -> str:
        return effective_target(self.mas, self.target_agent_name)

    def _build_agent_card(self, request_base_url: str) -> dict[str, Any]:
        card = build_agent_card(
            request_base_url=request_base_url,
            a2a_base_path=self.a2a_base_path,
            agent_version=self.agent_version,
            capabilities=self.capabilities,
            mas=self.mas,
            skills_override=self.skills,
        )
        logger.info(
            "A2A agent card built",
            extra={
                "a2a_base_path": self.a2a_base_path,
                "card_name": card.get("name", ""),
                "skills_count": len(card.get("skills", [])),
            },
        )
        return card

    def _build_mas_payload(
        self,
        *,
        text: str,
        context_id: str,
        task_id: str,
        reference_task_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        return build_mas_payload(
            text=text,
            context_id=context_id,
            task_id=task_id,
            target=self._effective_target(),
            reference_task_ids=reference_task_ids,
            metadata=metadata,
            context_session=self._store.context_session(context_id),
        )

    def _build_task(
        self,
        *,
        task_id: str,
        context_id: str,
        answer: str,
        trace_id: str,
        group_id: str,
        state: TaskState | str = TaskState.completed,
        error: str | None = None,
    ) -> dict[str, Any]:
        return self._store.build_task(
            task_id=task_id,
            context_id=context_id,
            answer=answer,
            trace_id=trace_id,
            group_id=group_id,
            state=state,
            error=error,
        )

    async def _invoke_mas_chat(
        self,
        *,
        text: str,
        context_id: str,
        task_id: str,
        reference_task_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[str, str, str]:
        """Invoke MAS chat and return ``(answer, trace_id, group_id)``."""
        if not self.mas:
            raise RuntimeError("MAS is not initialized.")

        payload = self._build_mas_payload(
            text=text,
            context_id=context_id,
            task_id=task_id,
            reference_task_ids=reference_task_ids,
            metadata=metadata,
        )
        if payload is None:
            # Avoid self-recursive routing when no target agent can be resolved.
            return text, task_id, context_id

        oxy_response = await self.mas.chat_with_agent(payload=payload)
        trace_id = str(oxy_response.oxy_request.current_trace_id)
        group_id = str(oxy_response.oxy_request.group_id)
        answer = str(oxy_response.output)

        self._store.save_context(
            context_id=context_id,
            group_id=group_id,
            trace_id=trace_id,
            task_id=task_id,
        )
        return answer, trace_id, group_id

    def build_router(self) -> APIRouter:
        """Build FastAPI router exposing A2A-compatible endpoints."""
        from sse_starlette.sse import EventSourceResponse

        router = APIRouter(prefix=self.a2a_base_path, tags=["a2a"])
        logger.info(
            "A2A router initialized", extra={"a2a_base_path": self.a2a_base_path}
        )

        @router.get("/.well-known/agent.json")
        async def get_agent_card(request: Request):
            return self._build_agent_card(str(request.base_url))

        async def run_send_message(payload: dict[str, Any]):
            msg_payload = self._normalize_message_payload(payload)
            text = self._extract_text(msg_payload)
            metadata = self._extract_metadata(payload)
            context_id, task_id = self._extract_context_and_task(payload, msg_payload)
            reference_task_ids = self._extract_reference_task_ids(payload, msg_payload)
            logger.info(
                "A2A message/send received",
                extra={
                    "context_id": context_id,
                    "task_id": task_id,
                    "has_reference_task_ids": bool(reference_task_ids),
                },
            )

            if self._store.is_running(task_id):
                logger.info("A2A task already running", extra={"task_id": task_id})
                task = self._store.get_task(task_id) or self._build_task(
                    task_id=task_id,
                    context_id=context_id,
                    answer="Task is running.",
                    trace_id=task_id,
                    group_id=context_id,
                    state=TaskState.working,
                )
                return task, "", task_id, context_id

            self._build_task(
                task_id=task_id,
                context_id=context_id,
                answer="Task is pending.",
                trace_id=task_id,
                group_id=context_id,
                state=TaskState.submitted,
            )
            self._store.mark_running(task_id)
            self._build_task(
                task_id=task_id,
                context_id=context_id,
                answer="Task is running.",
                trace_id=task_id,
                group_id=context_id,
                state=TaskState.working,
            )
            try:
                answer, trace_id, group_id = await self._invoke_mas_chat(
                    text=text,
                    context_id=context_id,
                    task_id=task_id,
                    reference_task_ids=reference_task_ids,
                    metadata=metadata,
                )
            except Exception as e:
                self._build_task(
                    task_id=task_id,
                    context_id=context_id,
                    answer=f"Task failed: {e}",
                    trace_id=task_id,
                    group_id=context_id,
                    state=TaskState.failed,
                    error=str(e),
                )
                logger.exception(
                    "A2A message/send failed",
                    extra={"task_id": task_id, "context_id": context_id},
                )
                raise RuntimeError(str(e))
            finally:
                self._store.unmark_running(task_id)

            task = self._build_task(
                task_id=task_id,
                context_id=context_id,
                answer=answer,
                trace_id=trace_id,
                group_id=group_id,
            )
            logger.info(
                "A2A message/send completed",
                extra={
                    "task_id": task_id,
                    "context_id": context_id,
                    "trace_id": trace_id,
                    "group_id": group_id,
                },
            )
            return task, answer, task_id, context_id

        async def run_send_message_stream(payload: dict[str, Any]):
            if not self.mas:
                raise RuntimeError("MAS is not initialized.")

            msg_payload = self._normalize_message_payload(payload)
            text = self._extract_text(msg_payload)
            metadata = self._extract_metadata(payload)
            context_id, task_id = self._extract_context_and_task(payload, msg_payload)
            reference_task_ids = self._extract_reference_task_ids(payload, msg_payload)
            logger.info(
                "A2A message/stream received",
                extra={
                    "context_id": context_id,
                    "task_id": task_id,
                    "has_reference_task_ids": bool(reference_task_ids),
                },
            )

            if self._store.is_running(task_id):
                logger.info(
                    "A2A stream task already running", extra={"task_id": task_id}
                )
                running_task = self._store.get_task(task_id)
                if running_task:
                    yield self._build_message_event(
                        running_task.get("status", {})
                        .get("message", {})
                        .get("parts", [{}])[0]
                        .get("text", ""),
                        task_id,
                        context_id,
                    )
                return

            payload_for_mas = self._build_mas_payload(
                text=text,
                context_id=context_id,
                task_id=task_id,
                reference_task_ids=reference_task_ids,
                metadata=metadata,
            )
            if payload_for_mas is None:
                self._build_task(
                    task_id=task_id,
                    context_id=context_id,
                    answer=text,
                    trace_id=task_id,
                    group_id=context_id,
                    state=TaskState.completed,
                )
                yield self._build_message_event(text, task_id, context_id)
                return

            self._build_task(
                task_id=task_id,
                context_id=context_id,
                answer="Task is pending.",
                trace_id=task_id,
                group_id=context_id,
                state=TaskState.submitted,
            )
            self._store.mark_running(task_id)
            self._build_task(
                task_id=task_id,
                context_id=context_id,
                answer="Task is running.",
                trace_id=task_id,
                group_id=context_id,
                state=TaskState.working,
            )

            redis_key = f"{self.mas.message_prefix}:{self.mas.name}:{task_id}"
            mas_task = asyncio.create_task(
                self.mas.chat_with_agent(
                    payload=payload_for_mas, send_msg_key=redis_key
                )
            )
            emitted = ""
            final_answer = ""
            last_snapshot_chars = 0
            last_snapshot_time = time.monotonic()
            try:
                async for sse_msg in self.mas._process_redis_messages(
                    redis_key, task_id
                ):
                    if sse_msg.get("event", "message") == "close":
                        break
                    data = sse_msg.get("data")
                    delta = self._extract_delta_from_sse_data(
                        data, parse_delta=self.parse_stream_delta
                    )
                    if not delta:
                        continue
                    emitted += delta
                    final_answer = emitted
                    should_refresh = False
                    if (
                        self.stream_task_update_char_interval > 0
                        and (len(emitted) - last_snapshot_chars)
                        >= self.stream_task_update_char_interval
                    ):
                        should_refresh = True
                    if (
                        self.stream_task_update_time_interval_seconds > 0
                        and (time.monotonic() - last_snapshot_time)
                        >= self.stream_task_update_time_interval_seconds
                    ):
                        should_refresh = True
                    if should_refresh:
                        self._build_task(
                            task_id=task_id,
                            context_id=context_id,
                            answer=emitted,
                            trace_id=task_id,
                            group_id=context_id,
                            state=TaskState.working,
                        )
                        last_snapshot_chars = len(emitted)
                        last_snapshot_time = time.monotonic()
                    yield self._build_message_event(emitted, task_id, context_id)

                oxy_response = await mas_task
                trace_id = str(oxy_response.oxy_request.current_trace_id)
                group_id = str(oxy_response.oxy_request.group_id)
                if not final_answer:
                    final_answer = str(oxy_response.output)
                    yield self._build_message_event(final_answer, task_id, context_id)

                self._build_task(
                    task_id=task_id,
                    context_id=context_id,
                    answer=final_answer,
                    trace_id=trace_id,
                    group_id=group_id,
                    state=TaskState.completed,
                )
                self._store.save_context(
                    context_id=context_id,
                    group_id=group_id,
                    trace_id=trace_id,
                    task_id=task_id,
                )
                logger.info(
                    "A2A message/stream completed",
                    extra={
                        "task_id": task_id,
                        "context_id": context_id,
                        "trace_id": trace_id,
                        "group_id": group_id,
                    },
                )
            except asyncio.CancelledError:
                self._build_task(
                    task_id=task_id,
                    context_id=context_id,
                    answer=final_answer or "Task canceled.",
                    trace_id=task_id,
                    group_id=context_id,
                    state=TaskState.canceled,
                )
                raise
            except Exception as e:
                self._build_task(
                    task_id=task_id,
                    context_id=context_id,
                    answer=f"Task failed: {e}",
                    trace_id=task_id,
                    group_id=context_id,
                    state=TaskState.failed,
                    error=str(e),
                )
                logger.exception(
                    "A2A message/stream failed",
                    extra={"task_id": task_id, "context_id": context_id},
                )
                raise RuntimeError(str(e))
            finally:
                self._store.unmark_running(task_id)

        async def run_get_task(task_id: str):
            if not task_id:
                raise ValueError("task id is required")
            task = self._store.get_task(task_id)
            if not task:
                logger.warning("A2A get_task not found", extra={"task_id": task_id})
                raise LookupError("task not found")
            return task

        async def run_cancel_task(task_id: str):
            task = await run_get_task(task_id)
            status = task.get("status", {}) if isinstance(task, dict) else {}
            message = status.get("message") if isinstance(status, dict) else None
            task["status"] = {"state": TaskState.canceled.value}
            if message:
                task["status"]["message"] = message
            self._store.unmark_running(task_id)
            logger.info("A2A task canceled", extra={"task_id": task_id})
            return task

        async def run_resubscribe(task_id: str):
            task = await run_get_task(task_id)
            message = (
                task.get("status", {})
                .get("message", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            context_id = task.get("contextId", "")
            return message, context_id

        def resolve_plain_action(payload: dict[str, Any]) -> str:
            action = str(
                payload.get("action")
                or payload.get("op")
                or payload.get("operation")
                or ""
            ).lower()
            if action:
                return action
            if payload.get("message") or payload.get("query"):
                return "send_message"
            if payload.get("taskId") or payload.get("id"):
                return "get_task"
            return ""

        async def handle_unified_post(payload: dict[str, Any]):
            if not isinstance(payload, dict):
                raise HTTPException(
                    status_code=400, detail="payload must be a JSON object"
                )

            method = payload.get("method")
            req_id = payload.get("id")
            logger.debug(
                "A2A unified POST received",
                extra={"method": method, "has_id": bool(req_id)},
            )

            if isinstance(method, str) and method:
                params = payload.get("params", {}) or {}

                if method == "message/send":
                    task, _, _, _ = await run_send_message(
                        params if isinstance(params, dict) else {}
                    )
                    return self._rpc_ok(req_id, task)

                if method == "message/stream":

                    async def stream_gen():
                        async for event in run_send_message_stream(
                            params if isinstance(params, dict) else {}
                        ):
                            yield {
                                "data": json.dumps(
                                    self._rpc_ok(req_id, event), ensure_ascii=False
                                )
                            }

                    return EventSourceResponse(stream_gen())

                try:
                    if method == "tasks/get":
                        task_id = params.get("id") or params.get("taskId")
                        return self._rpc_ok(
                            req_id, await run_get_task(str(task_id or ""))
                        )
                    if method == "tasks/cancel":
                        task_id = params.get("id") or params.get("taskId")
                        return self._rpc_ok(
                            req_id, await run_cancel_task(str(task_id or ""))
                        )
                    if method == "tasks/resubscribe":
                        task_id = params.get("id") or params.get("taskId")
                        msg, context_id = await run_resubscribe(str(task_id or ""))

                        async def resub_stream_gen():
                            event = self._build_message_event(
                                str(msg), str(task_id), context_id
                            )
                            yield {
                                "data": json.dumps(
                                    self._rpc_ok(req_id, event), ensure_ascii=False
                                )
                            }

                        return EventSourceResponse(resub_stream_gen())
                except ValueError as e:
                    logger.warning(
                        "A2A JSON-RPC validation error",
                        exc_info=True,
                        extra={"method": method, "error": str(e)},
                    )
                    return self._rpc_error(req_id, -32602, str(e))
                except LookupError as e:
                    logger.warning(
                        "A2A JSON-RPC lookup error",
                        exc_info=True,
                        extra={"method": method, "error": str(e)},
                    )
                    return self._rpc_error(req_id, -32004, str(e))
                except Exception as e:
                    logger.exception(
                        "A2A JSON-RPC unexpected error", extra={"method": method}
                    )
                    return self._rpc_error(req_id, -32000, str(e))

                return self._rpc_error(req_id, -32601, f"method `{method}` not found")

            action = resolve_plain_action(payload)
            action_alias = {
                "sendmessage": "send_message",
                "message/send": "send_message",
                "send_message": "send_message",
                "gettask": "get_task",
                "tasks/get": "get_task",
                "get_task": "get_task",
                "canceltask": "cancel_task",
                "tasks/cancel": "cancel_task",
                "cancel_task": "cancel_task",
                "resubscribe": "resubscribe",
                "tasks/resubscribe": "resubscribe",
            }
            action = action_alias.get(action, action)
            task_id = payload.get("id") or payload.get("taskId")

            try:
                if action == "send_message":
                    task, _, _, _ = await run_send_message(payload)
                    return {"task": task}
                if action == "get_task":
                    return {"task": await run_get_task(str(task_id or ""))}
                if action == "cancel_task":
                    return {"task": await run_cancel_task(str(task_id or ""))}
                if action == "resubscribe":
                    msg, context_id = await run_resubscribe(str(task_id or ""))
                    return {
                        "event": self._build_message_event(
                            str(msg), str(task_id), context_id
                        )
                    }
            except ValueError as e:
                logger.warning(
                    "A2A plain POST validation error",
                    exc_info=True,
                    extra={"action": action, "error": str(e)},
                )
                raise HTTPException(status_code=400, detail=str(e))
            except LookupError as e:
                logger.warning(
                    "A2A plain POST lookup error",
                    exc_info=True,
                    extra={"action": action, "error": str(e)},
                )
                raise HTTPException(status_code=404, detail=str(e))
            except RuntimeError as e:
                logger.warning(
                    "A2A plain POST runtime error",
                    exc_info=True,
                    extra={"action": action, "error": str(e)},
                )
                raise HTTPException(status_code=500, detail=str(e))

            raise HTTPException(
                status_code=400,
                detail=(
                    "unsupported action. use action in "
                    "send_message/get_task/cancel_task/resubscribe "
                    "or JSON-RPC method field"
                ),
            )

        @router.post("")
        async def unified_entry(request: Request):
            payload = await request.json()
            return await handle_unified_post(payload)

        @router.post("/")
        async def unified_entry_slash(request: Request):
            payload = await request.json()
            return await handle_unified_post(payload)

        @router.post("/messages/send")
        async def send_message(request: Request):
            payload = await request.json()
            payload.setdefault("action", "send_message")
            return await handle_unified_post(payload)

        @router.post("/messages/send/")
        async def send_message_slash(request: Request):
            payload = await request.json()
            payload.setdefault("action", "send_message")
            return await handle_unified_post(payload)

        @router.post("/tasks/get")
        async def get_task(request: Request):
            payload = await request.json()
            payload.setdefault("action", "get_task")
            return await handle_unified_post(payload)

        @router.post("/tasks/get/")
        async def get_task_slash(request: Request):
            payload = await request.json()
            payload.setdefault("action", "get_task")
            return await handle_unified_post(payload)

        @router.post("/tasks/cancel")
        async def cancel_task(request: Request):
            payload = await request.json()
            payload.setdefault("action", "cancel_task")
            return await handle_unified_post(payload)

        @router.post("/tasks/cancel/")
        async def cancel_task_slash(request: Request):
            payload = await request.json()
            payload.setdefault("action", "cancel_task")
            return await handle_unified_post(payload)

        return router
