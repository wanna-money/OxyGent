"""Mock LLM module for OxyGent.

Provides MockLLM, a deterministic stub useful for testing without invoking real models.
"""

import asyncio
from typing import Callable

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .base_llm import BaseLLM


class MockLLM(BaseLLM):
    """LLM stub that returns a configured mock response. Useful for unit testing."""

    func_mock_process: Callable = Field(
        None, exclude=True, description="Mock processing function"
    )

    def __init__(self, **kwargs):
        """Initialize the mock LLM."""
        super().__init__(**kwargs)

        if self.func_mock_process is None:
            self.func_mock_process = self._mock_process

    async def _mock_process(self, oxy_request: OxyRequest):
        """Apply optional user-defined processing to produce the mock response."""
        await asyncio.sleep(1)
        return "output"

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Return the configured mock output without contacting any real model."""
        output = await self.func_mock_process(oxy_request)
        return OxyResponse(state=OxyState.COMPLETED, output=output)
