"""llm.py LLM status module.

The module defines the status and the output of the LLM.
"""

from enum import Enum
from typing import Union

from pydantic import BaseModel, Field


class LLMState(Enum):
    """Enumeration of possible LLM response states."""

    TOOL_CALL = "tool_call"
    ANSWER = "answer"
    ERROR_PARSE = "error_parse"
    ERROR_CALL = "error_call"


class LLMResponse(BaseModel):
    """Container for the parsed response from an LLM call."""

    state: LLMState
    output: Union[str, list, dict]
    ori_response: str = Field(
        default="", description="Original raw LLM response text before parsing"
    )
