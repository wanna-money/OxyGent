"""Web response in base model."""

from typing import Any

from pydantic import BaseModel, Field


class WebResponse(BaseModel):
    """Standardized HTTP response wrapper for the web API."""

    code: int = Field(200, description="HTTP status code")
    message: str = Field("SUCCESS", description="Response status message")
    data: dict[str, Any] = Field(default_factory=dict, description="Response payload")

    def to_dict(self) -> dict[str, Any]:
        """Convert this response to a dictionary suitable for JSON serialization."""
        return self.model_dump()
