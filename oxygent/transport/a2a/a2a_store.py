"""In-memory runtime stores for A2A server gateway."""

from __future__ import annotations

from typing import Any

from .a2a_protocol import build_agent_message, build_final_artifact


class A2AInMemoryStore:
    """Track task snapshots, context state, and running markers."""

    def __init__(self):
        self.task_store: dict[str, dict[str, Any]] = {}
        self.context_store: dict[str, dict[str, Any]] = {}
        self.running_task_ids: set[str] = set()

    def context_session(self, context_id: str) -> dict[str, Any]:
        return self.context_store.get(context_id, {})

    def save_context(
        self, *, context_id: str, group_id: str, trace_id: str, task_id: str
    ) -> None:
        self.context_store[context_id] = {
            "group_id": group_id,
            "last_trace_id": trace_id,
            "last_task_id": task_id,
        }

    def is_running(self, task_id: str) -> bool:
        return task_id in self.running_task_ids

    def mark_running(self, task_id: str) -> None:
        self.running_task_ids.add(task_id)

    def unmark_running(self, task_id: str) -> None:
        self.running_task_ids.discard(task_id)

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self.task_store.get(task_id)

    def build_task(
        self,
        *,
        task_id: str,
        context_id: str,
        answer: str,
        trace_id: str,
        group_id: str,
        state: str = "completed",
    ) -> dict[str, Any]:
        """Build and cache task snapshot in memory."""
        task = {
            "kind": "task",
            "id": task_id,
            "contextId": context_id,
            "metadata": {"traceId": trace_id, "groupId": group_id},
        }
        if state == "completed":
            task["status"] = {
                "state": "completed",
                "message": build_agent_message(answer, task_id, context_id),
            }
            task["artifacts"] = [build_final_artifact(answer)]
        else:
            task["status"] = {
                "state": state,
                "message": build_agent_message(
                    answer or "Task is running.", task_id, context_id
                ),
            }
        self.task_store[task_id] = task
        return task
