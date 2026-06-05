"""Reflexion flow for iterative answer improvement.

Implements a generate-evaluate-refine loop: a worker agent produces an
answer, a reflexion agent evaluates it against quality criteria, and if
unsatisfactory the worker is prompted to improve.  The cycle repeats up
to ``max_reflexion_rounds`` times.  Also includes MathReflexion, a
math-specific variant with numeric evaluation templates.
"""

import logging
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

from ...schemas import Message, OxyRequest, OxyResponse, OxyState
from ...utils.llm_pydantic_parser import PydanticOutputParser
from ..base_flow import BaseFlow
from ..base_oxy import ensure_async

logger = logging.getLogger(__name__)


class ReflexionEvaluation(BaseModel):
    """Reflection evaluation result."""

    is_satisfactory: bool = Field(description="Whether the answer is satisfactory")
    evaluation_reason: str = Field(description="Detailed explanation of the evaluation")
    improvement_suggestions: str = Field(
        default="", description="Specific improvement suggestions if unsatisfactory"
    )


class Reflexion(BaseFlow):
    """Reflexion flow for iterative answer improvement.

    Orchestrates a worker agent and a reflexion (evaluator) agent in a loop:
    the worker generates an answer, the evaluator scores it, and if the
    answer is unsatisfactory the worker receives targeted feedback and
    tries again.

    Attributes:
        max_reflexion_rounds: Maximum number of generate-evaluate iterations.
        worker_agent: Name of the agent that produces answers.
        reflexion_agent: Name of the agent that evaluates answers.
        evaluation_template: Prompt template for the evaluation query.
        improvement_template: Prompt template for the improvement query.
    """

    max_reflexion_rounds: int = Field(3, description="Maximum reflexion iterations")

    worker_agent: str = Field("worker_agent", description="Worker agent name")
    reflexion_agent: str = Field("reflexion_agent", description="Reflexion agent name")

    # Custom parsing functions
    func_parse_worker_response: Optional[Callable[[str], str]] = (
        Field(  # Reflexion agent is optional; may be omitted
            None, exclude=True, description="Worker response parser"
        )
    )

    func_parse_reflexion_response: Optional[Callable[[str], ReflexionEvaluation]] = (
        Field(None, exclude=True, description="Reflexion response parser")
    )

    # Pydantic parsers
    pydantic_parser_reflexion: PydanticOutputParser = Field(
        default_factory=lambda: PydanticOutputParser(output_cls=ReflexionEvaluation),
        description="Reflexion pydantic parser",
    )

    # Evaluation templates
    evaluation_template: str = Field(
        default="""Please evaluate the quality of the following answer:

Original Question: {query}

Answer: {answer}

Please evaluate based on these criteria:
1. Accuracy: Is the information correct and factual?
2. Completeness: Does it fully address the user's question?
3. Clarity: Is it well-structured and easy to understand?
4. Relevance: Does it stay focused on the user's needs?
5. Helpfulness: Does it provide practical value to the user?

Return your evaluation in the following format:
- is_satisfactory: true/false
- evaluation_reason: [Detailed explanation]
- improvement_suggestions: [Specific recommendations if unsatisfactory]""",
        description="Template for evaluation query",
    )

    improvement_template: str = Field(
        default="""{original_query}

Please improve your previous answer based on the following feedback:
{improvement_suggestions}

Previous answer: {previous_answer}""",
        description="Template for improvement query",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the Reflexion flow with worker and evaluator agents."""
        super().__init__(**kwargs)

        self.add_permitted_tools(
            [
                self.worker_agent,
                self.reflexion_agent,
            ]
        )

        # Set default parsing functions if not provided
        if self.func_parse_worker_response is None:
            self.func_parse_worker_response = ensure_async(self._default_parse_worker_response)

        if self.func_parse_reflexion_response is None:
            self.func_parse_reflexion_response = ensure_async(self._default_parse_reflexion_response)

    def _default_parse_worker_response(self, response: str) -> str:
        """Default worker response parser - just return the response."""
        return response.strip()

    def _default_parse_reflexion_response(self, response: str) -> ReflexionEvaluation:
        """Default reflexion response parser."""
        if self.pydantic_parser_reflexion:
            return self.pydantic_parser_reflexion.parse(response)
        else:
            # Fallback parsing logic
            return self._parse_reflexion_text(response)

    def _parse_reflexion_text(self, response: str) -> ReflexionEvaluation:
        """Parse the evaluator LLM response into a ReflexionEvaluation.

        Falls back to line-by-line keyword matching when the pydantic
        parser is unavailable.

        Args:
            response: Raw text output from the reflexion agent.

        Returns:
            A ReflexionEvaluation with satisfaction flag and feedback.
        """
        lines = response.split("\n")

        is_satisfactory = False
        evaluation_reason = ""
        improvement_suggestions = ""

        for line in lines:
            line = line.strip()
            if "satisfactory" in line.lower():
                is_satisfactory = "unsatisfactory" not in line.lower()
            elif "evaluation result:" in line.lower():
                is_satisfactory = (
                    "satisfactory" in line.lower()
                    and "unsatisfactory" not in line.lower()
                )
            elif "evaluation reason:" in line.lower():
                evaluation_reason = line.split(":", 1)[-1].strip()
            elif "improvement suggestions:" in line.lower():
                improvement_suggestions = line.split(":", 1)[-1].strip()

        return ReflexionEvaluation(
            is_satisfactory=is_satisfactory,
            evaluation_reason=evaluation_reason or "No specific reason provided",
            improvement_suggestions=improvement_suggestions,
        )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Execute the reflexion loop.

        Runs the worker-evaluate-improve cycle until the answer is judged
        satisfactory or ``max_reflexion_rounds`` is exhausted.

        Args:
            oxy_request: The incoming request containing the user query.

        Returns:
            An OxyResponse with the final (possibly refined) answer.
        """

        original_query = oxy_request.get_query()
        current_query = original_query

        logger.info(f"Starting reflexion flow for query: {original_query}")

        for current_round in range(self.max_reflexion_rounds + 1):
            logger.info(f"Reflexion round {current_round + 1}")

            # Step 1: Get answer from worker agent
            worker_response = await oxy_request.call(
                callee=self.worker_agent, arguments={"query": current_query}
            )

            current_answer = await self.func_parse_worker_response(worker_response.output)
            logger.info(f"Worker answer: {current_answer[:200]}...")

            # Step 2: Evaluate with reflexion agent
            evaluation_query = self.evaluation_template.format(
                query=original_query, answer=current_answer
            )

            if self.pydantic_parser_reflexion:
                evaluation_query = self.pydantic_parser_reflexion.format(
                    evaluation_query
                )

            reflexion_response = await oxy_request.call(
                callee=self.reflexion_agent, arguments={"query": evaluation_query}
            )

            evaluation = await self.func_parse_reflexion_response(reflexion_response.output)
            logger.info(f"Evaluation result: {evaluation.is_satisfactory}")

            # Step 3: Check if satisfactory
            if evaluation.is_satisfactory:
                logger.info(f"Answer satisfactory after {current_round + 1} rounds")
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=f"Final answer optimized through {current_round + 1} rounds of reflexion:\n\n{current_answer}",
                    extra={
                        "reflexion_rounds": current_round + 1,
                        "final_evaluation": evaluation.model_dump(),
                    },
                )

            # Step 4: If not satisfactory and not last round, prepare improvement query
            if current_round < self.max_reflexion_rounds:
                if evaluation.improvement_suggestions:
                    current_query = self.improvement_template.format(
                        original_query=original_query,
                        improvement_suggestions=evaluation.improvement_suggestions,
                        previous_answer=current_answer,
                    )
                    logger.info(
                        f"Updated query with improvements: {evaluation.improvement_suggestions}"
                    )
                else:
                    # If no specific suggestions, just retry with original query
                    current_query = f"{original_query}\n\nPlease provide a better answer. Previous attempt was: {evaluation.evaluation_reason}"

        # Reached maximum rounds without satisfaction
        logger.warning(
            f"Reached maximum reflexion rounds ({self.max_reflexion_rounds + 1})"
        )

        # Generate final answer using LLM with accumulated feedback
        final_query = f"""
Original user question: {original_query}

Latest answer attempt: {current_answer}

Latest evaluation feedback: {evaluation.evaluation_reason}

Please provide the best possible final answer considering all the feedback above.
"""

        final_messages = [
            Message.system_message(
                "You are tasked with providing the best possible answer based on previous attempts and feedback."
            ),
            Message.user_message(final_query),
        ]

        final_response = await oxy_request.call(
            callee=self.llm_model,
            arguments={"messages": [msg.to_dict() for msg in final_messages]},
        )

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=f"Answer after {self.max_reflexion_rounds + 1} rounds of reflexion attempts:\n\n{final_response.output}",
            extra={
                "reflexion_rounds": self.max_reflexion_rounds + 1,
                "final_evaluation": evaluation.model_dump(),
                "reached_max_rounds": True,
            },
        )


class MathReflexion(Reflexion):
    """Math-specific Reflexion flow with numeric answer comparison.

    Pre-configures the worker and evaluator agents and evaluation template
    for mathematical problem-solving, with checks for calculation
    correctness, step completeness, and formula accuracy.
    """

    def __init__(self, **kwargs: Any) -> None:
        # Set default agents for math problems
        if "worker_agent" not in kwargs:
            kwargs["worker_agent"] = "math_expert_agent"
        if "reflexion_agent" not in kwargs:
            kwargs["reflexion_agent"] = "math_checker_agent"

        # Set math-specific evaluation template
        if "evaluation_template" not in kwargs:
            kwargs[
                "evaluation_template"
            ] = """Please check the correctness and completeness of the following mathematical solution:

Problem: {query}

Solution: {answer}

Check points:
1. Are the calculation steps correct?
2. Are there any missing steps?
3. Is the final answer clear?
4. Is the problem-solving approach clear?
5. Are mathematical formulas and theorems applied correctly?

Return your evaluation in the following format:
- is_satisfactory: true/false (use true for Pass, false for Fail)
- evaluation_reason: [Detailed explanation of the check]
- improvement_suggestions: [Specific correction suggestions if failed]"""

        super().__init__(**kwargs)
