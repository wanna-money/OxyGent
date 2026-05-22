"""Mock LLM module for OxyGent.

Provides MockLLM, a deterministic stub useful for testing without invoking real models.
"""

import asyncio
from typing import Any, Callable

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .base_llm import BaseLLM


class MockLLM(BaseLLM):
    """LLM stub that returns a configured mock response.

    Useful for unit testing agents and flows without calling a real model.
    The response can be customised by supplying a ``func_mock_process``
    callable at construction time.

    Attributes:
        func_mock_process: Async callable that produces the mock output
            string given an OxyRequest. Defaults to an internal stub that
            sleeps for 1 second and returns ``"output"``.
    """

    func_mock_process: Callable = Field(
        None, exclude=True, description="Mock processing function"
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the mock LLM."""
        super().__init__(**kwargs)

        if self.func_mock_process is None:
            self.func_mock_process = self._mock_process

    async def _mock_process(self, oxy_request: OxyRequest) -> str:
        """Default mock processor that returns a fixed string after a short delay.

        Args:
            oxy_request: The incoming request (ignored by the default stub).

        Returns:
            The literal string ``"output"``.
        """
        await asyncio.sleep(1)
        return "output"

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Return the configured mock output without contacting any real model.

        Args:
            oxy_request: The incoming request forwarded to ``func_mock_process``.

        Returns:
            An OxyResponse with COMPLETED state and the mock output string.
        """
        output = await self.func_mock_process(oxy_request)
        return OxyResponse(state=OxyState.COMPLETED, output=output)
