"""LLM output parser using Pydantic models for structured output extraction."""

import json
from typing import Any, Optional

from pydantic import BaseModel

from ..utils.common_utils import extract_json_str

PYDANTIC_FORMAT_TMPL = """
Here's a JSON schema to follow:
{schema}

Output a valid JSON object but do not repeat the schema.
Omit any markdown formatting.
Do not include any other text than the JSON object.
Do not include any preamble or explanation.
Do not repeat the schema.
"""


class PydanticOutputParser(BaseModel):
    """Parses LLM text output into validated Pydantic model instances.

    Attributes:
        output_cls: The target Pydantic model class for deserialization.
    """

    def __init__(
        self,
        output_cls: type[BaseModel],
        excluded_schema_keys_from_format: Optional[list[str]] = None,
        pydantic_format_tmpl: str = PYDANTIC_FORMAT_TMPL,
    ) -> None:
        """Initialize the parser.

        Args:
            output_cls: Pydantic model class defining the expected output schema.
            excluded_schema_keys_from_format: Schema keys to omit from the
                format instruction shown to the LLM.
            pydantic_format_tmpl: Template string for the JSON schema prompt.
        """
        self._output_cls = output_cls
        self._excluded_schema_keys_from_format = excluded_schema_keys_from_format or []
        self._pydantic_format_tmpl = pydantic_format_tmpl

    @property
    def output_cls(self) -> type[BaseModel]:
        return self._output_cls

    @property
    def format_string(self) -> str:
        """The schema instruction string with braces escaped for ``str.format()``."""
        return self.get_format_string(escape_json=True)

    def get_format_string(self, escape_json: bool = True) -> str:
        """Build the JSON schema instruction string for LLM prompts.

        Args:
            escape_json: Whether to escape braces for ``str.format()`` compatibility.

        Returns:
            The formatted schema instruction string.
        """
        schema_dict = self._output_cls.model_json_schema()
        for key in self._excluded_schema_keys_from_format:
            del schema_dict[key]

        schema_str = json.dumps(schema_dict)
        output_str = self._pydantic_format_tmpl.format(schema=schema_str)
        if escape_json:
            return output_str.replace("{", "{{").replace("}", "}}")
        else:
            return output_str

    def parse(self, text: str) -> Any:
        """Parse, validate, and correct errors programmatically."""
        json_str = extract_json_str(text)
        return self._output_cls.model_validate_json(json_str)

    def format(self, query: str) -> str:
        """Format a query with structured output formatting instructions."""
        return query + "\n\n" + self.get_format_string(escape_json=True)
