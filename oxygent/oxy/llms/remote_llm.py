"""Remote LLM base class for OxyGent.

Provides RemoteLLM, the abstract base class for any LLM accessed over the network
(HTTP/OpenAI-compatible APIs, etc.).
"""

from typing import Callable, Dict, Optional

from pydantic import Field, field_validator

from ...schemas import OxyRequest, OxyResponse
from .base_llm import BaseLLM


class RemoteLLM(BaseLLM):
    """Abstract base class for LLMs that are accessed over the network.

    Subclasses (e.g., HttpLLM, OpenAILLM) implement provider-specific request
    formatting and response parsing."""

    api_key: Optional[str] = Field(
        default=None,
        description="API key for authenticating with the remote LLM service",
    )
    base_url: Optional[str] = Field(
        "", description="Base URL of the remote LLM API endpoint"
    )
    model_name: Optional[str] = Field(
        "", description="Model identifier to use for requests"
    )
    headers: Dict[str, str] | Callable[[OxyRequest], Dict[str, str]] = Field(
        default=lambda oxy_request: {},
        exclude=True,
        description="Extra HTTP headers or a function that returns headers",
    )

    @field_validator("base_url", "model_name")
    @classmethod
    def not_empty(cls, value, info):
        """Pydantic field validator: forbid empty/null required values."""
        key = info.field_name

        if value is None:
            raise ValueError(
                f"Environment variable '{key}' is not set and no default value provided. Please check your .env or system env."
            )

        if not isinstance(value, str):
            raise ValueError(
                f"Environment variable '{key}' type error: expected str, got {type(value).__name__}."
            )

        if not value.strip():
            raise ValueError(f"{key} must be a non-empty string")

        return value

    @field_validator("headers")
    @classmethod
    def convert_dict_to_function(cls, v):
        """Automatically wrap a dict value into a callable returning that dict."""
        if isinstance(v, dict):
            # Wrap dict into a function that returns it
            def headers_func(request: OxyRequest) -> Dict[str, str]:
                return v

            return headers_func
        elif callable(v):
            # Return as-is when value is already callable
            return v
        else:
            raise ValueError("headers must be either a dict or a callable")

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Subclasses must implement provider-specific request execution."""
        raise NotImplementedError("This method is not yet implemented")
