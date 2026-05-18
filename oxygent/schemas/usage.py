"""Token usage tracking schemas."""

from enum import Enum

from pydantic import BaseModel, Field, computed_field


class EstimationMethod(str, Enum):
    """Token estimation method."""

    EXACT = "exact"  # API returned exact value
    TIKTOKEN = "tiktoken"  # tiktoken estimation
    APPROXIMATE = "approximate"  # character count estimation


class TokenUsage(BaseModel):
    """Token usage information for a single LLM call.

    Attributes:
        input_tokens: Number of input (prompt) tokens.
        output_tokens: Number of output (completion) tokens.
        cached_tokens: Number of input tokens served from cache (e.g. OpenAI
            prompt_tokens_details.cached_tokens, Anthropic cache_read_input_tokens).
        reasoning_tokens: Number of tokens used for reasoning/thinking
            (e.g. OpenAI completion_tokens_details.reasoning_tokens).
        model_name: Name of the LLM model used.
        estimation_method: Method used for token counting.
    """

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cached_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    model_name: str = ""
    estimation_method: EstimationMethod = EstimationMethod.EXACT

    @computed_field
    @property
    def total_tokens(self) -> int:
        """Total tokens (input + output), always computed."""
        return self.input_tokens + self.output_tokens
