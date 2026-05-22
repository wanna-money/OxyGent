"""In-memory runtime stores for the A2A server gateway.

Provides ``A2AInMemoryStore`` which tracks task snapshots, per-context session
state, and running-task markers during the lifetime of the gateway process.
"""

from __future__ import annotations

from typing import Any

from a2a.types import TaskState

from .a2a_protocol import build_agent_message, build_final_artifact


class A2AInMemoryStore:
    """In-memory store for A2A task snapshots, context sessions, and run state.

    Attributes:
        task_store: Mapping of task_id to the latest task snapshot dict.
        context_store: Mapping of context_id to session metadata (group_id,
            last_trace_id, last_task_id).
        running_task_ids: Set of task IDs currently being processed.
    """

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
        state: TaskState | str = TaskState.completed,
        error: str | None = None,
    ) -> dict[str, Any]:
        """Build a task snapshot dict and cache it in the store.

        Constructs the appropriate status, message, artifacts, and error
        fields based on the task state, then persists the snapshot in
        ``task_store``.

        Args:
            task_id: Unique task identifier.
            context_id: Associated context identifier.
            answer: Answer text or status message.
            trace_id: MAS trace identifier.
            group_id: MAS group identifier.
            state: Task lifecycle state. Defaults to ``completed``.
            error: Optional error message for failed tasks.

        Returns:
            Complete task snapshot dictionary.
        """
        state_value = (
            state.value
            if isinstance(state, TaskState)
            else str(state or TaskState.unknown.value)
        )
        if state_value == "pending":
            state_value = TaskState.submitted.value

        task = {
            "kind": "task",
            "id": task_id,
            "contextId": context_id,
            "metadata": {"traceId": trace_id, "groupId": group_id},
        }
        if state_value == TaskState.completed.value:
            task["status"] = {
                "state": state_value,
                "message": build_agent_message(answer, task_id, context_id),
            }
            task["artifacts"] = [build_final_artifact(answer)]
            task["result"] = {"output": answer}
        elif state_value == TaskState.failed.value:
            msg = error or answer or "Task failed."
            task["status"] = {
                "state": state_value,
                "message": build_agent_message(msg, task_id, context_id),
            }
            task["error"] = {"message": msg}
        else:
            task["status"] = {
                "state": state_value,
                "message": build_agent_message(
                    answer or "Task is processing.", task_id, context_id
                ),
            }
        self.task_store[task_id] = task
        return task
