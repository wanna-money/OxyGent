"""Base Bank module for OxyGent.

Provides a base class for bank tools — namespace containers for grouping related
FastAPI-router-based tools.
"""

import logging

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse
from ..base_tool import BaseTool

logger = logging.getLogger(__name__)


class BaseBank(BaseTool):
    """Abstract base class for bank tools (FastAPI-router-based tool collections)."""

    category: str = Field(
        "bank", description="Category identifier, always 'bank' for bank tools"
    )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Subclasses must implement bank-specific dispatch logic.

        Args:
            oxy_request: The incoming request to dispatch.

        Raises:
            NotImplementedError: Always, unless overridden by a subclass.
        """
        raise NotImplementedError("This method is not yet implemented")
