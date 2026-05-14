"""Workflow agent module for custom workflow execution.

This module provides the WorkflowAgent class, which enables execution of custom workflow
functions within the OxyGent framework. It serves as a bridge between the agent system
and user-defined workflow logic.
"""

from typing import Callable, Optional

from pydantic import Field

from ...schemas import OxyRequest, OxyResponse, OxyState
from .local_agent import LocalAgent


class WorkflowAgent(LocalAgent):
    """Agent that executes custom workflow functions.

    This agent provides a flexible way to integrate custom workflow logic
    into the OxyGent system.

    Attributes:
        func_workflow (Optional[Callable]): The workflow function to execute.
            This function should accept an OxyRequest and return the result.
    """

    func_workflow: Optional[Callable] = Field(
        None, exclude=True, description="Custom workflow function to execute"
    )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute the user-defined workflow function."""
        if self.func_workflow is None:
            return OxyResponse(
                state=OxyState.FAILED,
                output=f"WorkflowAgent '{self.name}' has no func_workflow defined.",
            )
        return OxyResponse(
            state=OxyState.COMPLETED, output=await self.func_workflow(oxy_request)
        )
