"""RAG agent module.

Provides the RAGAgent class which augments LLM responses with retrieved context."""

from typing import Callable

from pydantic import Field, model_validator

from ...schemas.oxy import OxyRequest
from .chat_agent import ChatAgent


class RAGAgent(ChatAgent):
    """A retrieval-augmented agent that fetches relevant context before LLM generation."""

    knowledge_placeholder: str = Field("knowledge")

    func_retrieve_knowledge: Callable = Field(
        exclude=True, description="Retrieve knowledge function"
    )

    @model_validator(mode="after")
    def set_default_prompt(self) -> "RAGAgent":
        """Pydantic model validator that injects the default RAG prompt if none provided."""
        if not self.prompt:
            self.prompt = (
                "You are a helpful assistant. You can refer to the following information to answer the questions.\n${"
                + self.knowledge_placeholder
                + "}"
            )
        return self

    async def _pre_process(self, oxy_request: OxyRequest) -> OxyRequest:
        """Retrieve relevant context and inject it into the request before execution."""
        oxy_request = await super()._pre_process(oxy_request)
        knowledge = await self.func_retrieve_knowledge(oxy_request)
        oxy_request.arguments[self.knowledge_placeholder] = knowledge
        return oxy_request
