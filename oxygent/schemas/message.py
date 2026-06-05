"""Server-Sent Events (SSE) message schema.

Provides the SSEMessage model used to push events to connected web clients
through the EventSource protocol.
"""

from typing import Any

from pydantic import BaseModel, Field

from ..utils.common_utils import generate_uuid, to_json


class SSEMessage(BaseModel):
    """Message wrapper for Server-Sent Events streaming."""

    id: str = Field(
        default_factory=generate_uuid, description="Unique message identifier"
    )
    event: str = Field("message", description="SSE event type")
    data: Any = Field("", description="Message payload")
    retry: int = Field(3000, description="Client reconnection interval in milliseconds")

    def to_sse(self) -> dict[str, Any]:
        """Serialize this message to SSE wire format."""
        return {
            "id": self.id,
            "event": self.event,
            "data": to_json(self.data),
            "retry": self.retry,
        }
