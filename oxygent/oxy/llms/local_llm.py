"""Local LLM module for OxyGent.

Provides LocalLLM which loads and runs a HuggingFace transformer model locally.
"""

import logging

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .base_llm import BaseLLM

logger = logging.getLogger(__name__)


class LocalLLM(BaseLLM):
    """LLM that loads a transformer model from disk and runs inference locally."""

    model_path: str = Field("")
    device_map: str = Field("auto")
    dtype: str = Field("bfloat16")

    async def init(self) -> None:
        """Load the model and tokenizer from the configured path."""
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as e:
            raise ImportError(
                "LocalLLM requires 'torch' and 'transformers' packages."
                "Please install them using 'pip install torch transformers einops transformers_stream_generator accelerate'"
            ) from e

        await super().init()
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_path, device_map=self.device_map, dtype=self.dtype
        )
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Generate a response by running the local model on the input messages."""
        payload = {}
        self._build_payload(oxy_request, payload)

        replace_dict = {
            "max_tokens": "max_new_tokens",
            "stream": "",
        }
        for k, v in replace_dict.items():
            if k in payload:
                if v:
                    payload[v] = payload[k]
                del payload[k]

        messages = oxy_request.arguments["messages"]

        input_text = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        input_ids = self._tokenizer.encode(input_text, return_tensors="pt")
        input_ids = input_ids.to(self._model.device)
        outputs = self._model.generate(input_ids=input_ids, **payload)[0]
        outputs = outputs[len(input_ids[0]) :]

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=self._tokenizer.decode(outputs, skip_special_tokens=True),
        )
