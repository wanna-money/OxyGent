"""Function tool implementations for OxyGent.

Provides FunctionHub (decorator-based registration) and FunctionTool
(individual function wrapper) for exposing Python functions as agent tools.
"""

from .function_hub import FunctionHub
from .function_tool import FunctionTool

__all__ = [
    "FunctionHub",
    "FunctionTool",
]
