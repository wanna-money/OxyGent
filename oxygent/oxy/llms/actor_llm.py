"""Actor LLM module for OxyGent."""

import asyncio
import logging
import os
from typing import Any

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .base_llm import BaseLLM

logger = logging.getLogger(__name__)


def _generated_ids_to_jsonable(generated_ids):
    """Convert tensor values to plain lists so that ES JSON serialization is lossless.

    Without this, json.dumps(..., default=str) stores str(tensor), which torch
    truncates with "..." for tensors longer than 1000 elements, corrupting the
    token ids beyond recovery.
    """
    if not isinstance(generated_ids, dict):
        return generated_ids
    jsonable = dict(generated_ids)
    for key, value in jsonable.items():
        if hasattr(value, "tolist"):
            jsonable[key] = value.tolist()
    return jsonable


def _ray_get_sync(obj_refs, timeout=None):
    use_ray = os.getenv("USE_RAY")
    if use_ray:
        import ray
    else:
        import ray_adapter as ray

    if timeout is not None and timeout > 0:
        if use_ray:
            return ray.get(obj_refs, timeout=float(timeout))
        return ray.get(obj_refs, timeout=max(1, int(float(timeout) * 1000)))
    return ray.get(obj_refs)


async def _ray_get(obj_refs, timeout=None):
    return await asyncio.to_thread(_ray_get_sync, obj_refs, timeout)


class ActorLLM(BaseLLM):
    """LLM that loads a transformer model from disk and runs inference locally."""

    actor_llm: Any = Field(None)
    name: str = Field("llm")
    actor_llm_timeout: float = Field(0.0)
    raise_on_error: bool = Field(True)

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Generate a response by running the local model on the input messages."""
        messages = list(oxy_request.arguments["messages"])

        system_messages = [
            message for message in messages if message.get("role") == "system"
        ]
        if not system_messages:
            raise ValueError("input system prompt missing")
        prompt = "\n\n".join(
            str(message.get("content") or "") for message in system_messages
        )

        user_message_indexes = [
            index
            for index, message in enumerate(messages)
            if message.get("role") == "user"
        ]
        if not user_message_indexes:
            raise ValueError("input user query missing")
        query_index = user_message_indexes[-1]
        query = messages[query_index].get("content")
        history = [
            message
            for index, message in enumerate(messages)
            if message.get("role") != "system" and index != query_index
        ]

        try:
            obj_refs = self.actor_llm.agent_generate_one_step(
                query, history, prompt, "user"
            )
            timeout = float(
                os.getenv("OXYGENT_ACTOR_LLM_TIMEOUT", self.actor_llm_timeout)
            )
            response, generated_ids, history = await _ray_get(obj_refs, timeout=timeout)
        except Exception as err:
            actor_name = getattr(
                getattr(self.actor_llm, "workers", None), "pool_name", self.name
            )
            logger.error(
                f"[{actor_name}] agent_generate_one_step failed or timed out",
                exc_info=True,
            )
            should_raise = os.getenv("OXYGENT_ACTOR_LLM_RAISE_ON_ERROR", "1") != "0"
            if self.raise_on_error and should_raise:
                raise RuntimeError(
                    f"[{actor_name}] agent_generate_one_step failed or timed out"
                ) from err
            return OxyResponse(
                state=OxyState.FAILED,
                output=f"[{actor_name}] agent_generate_one_step failed",
            )

        ## todo: ------ Ray REGION END ------
        if not response or not generated_ids:
            actor_name = getattr(
                getattr(self.actor_llm, "workers", None), "pool_name", self.name
            )
            message = (
                f"[{actor_name}] agent_generate_one_step failed to return "
                "response or generated_ids"
            )
            if self.raise_on_error:
                raise RuntimeError(message)
            logger.error(message)
            return OxyResponse(
                state=OxyState.FAILED,
                output=message,
            )

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=response,
            extra={"generated_ids": _generated_ids_to_jsonable(generated_ids)},
        )
