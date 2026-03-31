"""OpenAI LLM implementation using the official OpenAI Python client.

This module provides the OpenAILLM class, which implements the BaseLLM interface
specifically for OpenAI's language models using the official AsyncOpenAI client. It
supports all OpenAI models and compatible APIs.
"""

import logging
from typing import Optional

from openai import AsyncOpenAI
from pydantic import PrivateAttr

from ...config import Config
from ...schemas import OxyRequest, OxyResponse, OxyState
from .remote_llm import RemoteLLM

logger = logging.getLogger(__name__)


class OpenAILLM(RemoteLLM):
    """OpenAI Large Language Model implementation.

    This class provides a concrete implementation of RemoteLLM specifically designed
    for OpenAI's language models. It uses the official AsyncOpenAI client for
    optimal performance and compatibility with OpenAI's API standards.

    The client instance is lazily created and reused across requests.
    """

    _client: Optional[AsyncOpenAI] = PrivateAttr(default=None)

    def _get_client(self) -> AsyncOpenAI:
        """Get or create a lazily-initialized AsyncOpenAI client."""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute a request using the OpenAI API.

        Creates a chat completion request using the official AsyncOpenAI client.
        The method handles payload construction, configuration merging, and
        response processing for OpenAI's chat completion API.

        Args:
            oxy_request: The request object containing messages and parameters.

        Returns:
            OxyResponse: The response containing the model's output with COMPLETED state.
        """
        messages = await self._get_messages(oxy_request)
        # Construct payload for OpenAI API request
        payload = {
            "messages": messages,
            "model": self.model_name,
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        payload.update(Config.get_llm_config(exclude=["semaphore", "timeout"]))
        for k, v in self.llm_params.items():
            payload[k] = v
        for k, v in oxy_request.arguments.items():
            if k == "messages":
                continue
            payload[k] = v

        client = self._get_client()
        completion = await client.chat.completions.create(**payload)
        if payload["stream"]:
            answer = ""
            think_start = True
            think_end = False
            usage_data = None
            char = None
            async for chunk in completion:
                # Extract usage from final chunk (choices is empty for usage-only chunks)
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
