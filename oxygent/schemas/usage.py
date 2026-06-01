"""Token usage tracking schemas."""

from enum import Enum

from pydantic import BaseModel, Field, model_validator


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
        cached_input_tokens: Number of input tokens served from cache read hit.
            (e.g. OpenAI prompt_tokens_details.cached_tokens,
            Anthropic cache_read_input_tokens, DeepSeek prompt_cache_hit_tokens,
            Gemini cachedContentTokenCount).
        cache_creation_input_tokens: Number of input tokens written to cache.
            (e.g. Anthropic cache_creation_input_tokens).
        reasoning_tokens: Number of tokens used for reasoning/thinking.
        model_name: Name of the LLM model used.
        estimation_method: Method used for token counting.
    """

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    cache_creation_input_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    model_name: str = ""
    estimation_method: EstimationMethod = EstimationMethod.EXACT

    @model_validator(mode="after")
    def _compute_total(self) -> "TokenUsage":
        """Use API-provided total_tokens when available, fallback to input+output."""
        if self.total_tokens == 0:
            self.total_tokens = self.input_tokens + self.output_tokens
        return self
