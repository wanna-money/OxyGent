from pydantic import BaseModel, Field

from ..utils.common_utils import to_json
from .oxy import OxyOutput, OxyResponse


class ExecResult(BaseModel):
    """Represents the result of a single tool execution."""

    executor: str
    oxy_response: OxyResponse


class Observation(BaseModel):
    """Observation for multimodal."""

    exec_results: list[ExecResult] = Field(
        default_factory=list, description="List of individual tool execution results"
    )

    def add_exec_result(self, exec_result: ExecResult) -> None:
        """Add an exec result to exec_results."""
        self.exec_results.append(exec_result)

    def to_str(self, is_prefix_included: bool = True) -> str:
        """Format all execution results as a human-readable string."""
        outs = []
        for exec_result in self.exec_results:
            if is_prefix_included:
                prefix = f"Tool [{exec_result.executor}] execution result: "
            else:
                prefix = ""
            if isinstance(exec_result.oxy_response.output, OxyOutput):
                outs.append(prefix + to_json(exec_result.oxy_response.output.result))
            else:
                outs.append(prefix + to_json(exec_result.oxy_response.output))
        return "\n\n".join(outs)
