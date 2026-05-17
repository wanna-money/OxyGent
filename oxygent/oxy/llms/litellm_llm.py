"""LiteLLM provider for OxyGent.

Supports 100+ LLM providers (OpenAI, Anthropic, Google, Azure, AWS Bedrock, Ollama,
etc.) through a single unified interface via the LiteLLM library.
"""

import logging
from typing import Optional

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .base_llm import BaseLLM

logger = logging.getLogger(__name__)


class LiteLLMLLM(BaseLLM):
    """LLM provider via LiteLLM -- supports 100+ providers through a unified API.

    Uses ``litellm.acompletion`` under the hood, which accepts the same
    message format as OpenAI and routes to the correct provider based on
    the ``model_name`` prefix (e.g. ``anthropic/claude-sonnet-4-20250514``,
    ``openai/gpt-4o``, ``bedrock/anthropic.claude-3``).

    The ``litellm`` package must be installed separately::

        pip install litellm
    """

    api_key: Optional[str] = Field(
        default=None,
        description="API key for the underlying provider. When unset, LiteLLM "
        "falls back to provider-specific env vars (ANTHROPIC_API_KEY, etc.).",
    )
    model_name: str = Field(
        ...,
        description="LiteLLM model identifier, e.g. 'anthropic/claude-sonnet-4-20250514'",
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Optional base URL for a LiteLLM proxy server.",
    )
    drop_params: bool = Field(
        default=True,
        description="Silently drop provider-unsupported params (recommended).",
    )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute a request via litellm.acompletion."""
        try:
            import litellm
        except ImportError:
            raise ImportError(
                "litellm is required for LiteLLMLLM. "
                "Install it with: pip install litellm"
            )

        messages = await self._get_messages(oxy_request)
        payload = {
            "messages": messages,
            "model": self.model_name,
            "stream": True,
            "stream_options": {"include_usage": True},
            "drop_params": self.drop_params,
        }
        if self.api_key:
            payload["api_key"] = self.api_key
        if self.base_url:
            payload["api_base"] = self.base_url

        self._build_payload(oxy_request, payload)

        completion = await litellm.acompletion(**payload)
        if payload["stream"]:
            answer = ""
            think_start = True
            think_end = False
            usage_data = None
            char = None
            async for chunk in completion:
                if hasattr(chunk, "usage") and chunk.usage:
                    usage_data = chunk.usage
                if not chunk.choices:
                    continue
                if hasattr(chunk.choices[0].delta, "reasoning_content"):
                    if think_start:
                        await oxy_request.send_message(
                            {
                                "type": "stream",
                                "content": {
                                    "delta": "<think>",
                                    "agent": oxy_request.caller,
                                    "node_id": oxy_request.node_id,
                                },
                            }
                        )
                        answer += "<think>"
                        think_start = False
                        think_end = True
                    char = chunk.choices[0].delta.reasoning_content
                elif hasattr(chunk.choices[0].delta, "content"):
                    if think_end:
                        await oxy_request.send_message(
                            {
                                "type": "stream",
                                "content": {
                                    "delta": "</think>",
                                    "agent": oxy_request.caller,
                                    "node_id": oxy_request.node_id,
                                },
                            }
                        )
                        answer += "</think>"
                        think_end = False
                    char = chunk.choices[0].delta.content
                else:
                    char = None
                if char:
                    answer += char
                    await oxy_request.send_message(
                        {
                            "type": "stream",
                            "content": {
                                "delta": char,
                                "agent": oxy_request.caller,
                                "node_id": oxy_request.node_id,
                            },
                        }
                    )
            await oxy_request.send_message(
                {
                    "type": "stream_end",
                    "content": {
                        "delta": "",
                        "agent": oxy_request.caller,
                        "node_id": oxy_request.node_id,
                    },
                }
            )
            token_usage = self._build_token_usage(usage_data, messages, answer)
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=answer,
                extra={"usage": token_usage},
            )
        else:
            output = completion.choices[0].message.content
            usage_data = getattr(completion, "usage", None)
            token_usage = self._build_token_usage(usage_data, messages, output)
            return OxyResponse(
                state=OxyState.COMPLETED,
                output=output,
                extra={"usage": token_usage},
            )
