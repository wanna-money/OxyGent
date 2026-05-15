"""Unit tests for oxygent.oxy_factory (OxyFactory, SecurityError)."""

import pytest

from oxygent.oxy_factory import OxyFactory, SecurityError


# ──────────────────────────────────────────────────────────────────────────────
# Dangerous class names should be blocked
# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "class_name",
    [
        "ChatAgent",
        "ReActAgent",
        "WorkflowAgent",
        "HttpTool",
        "MCPTool",
        "StdioMCPClient",
        "SSEMCPClient",
        "FunctionTool",
        "Workflow",
    ],
)
def test_dangerous_classes_raise_security_error(class_name):
    with pytest.raises(SecurityError, match="not allowed"):
        OxyFactory.create_oxy(class_name)


# ──────────────────────────────────────────────────────────────────────────────
# Unknown class names should be blocked
# ──────────────────────────────────────────────────────────────────────────────
def test_unknown_class_raises_security_error():
    with pytest.raises(SecurityError, match="Unknown class"):
        OxyFactory.create_oxy("NonExistentClass")


# ──────────────────────────────────────────────────────────────────────────────
# Allowed classes can be created
# ──────────────────────────────────────────────────────────────────────────────
def test_allowed_classes_in_creators():
    """HttpLLM and OpenAILLM should be in _creators and not blocked."""
    assert "HttpLLM" in OxyFactory._creators
    assert "OpenAILLM" in OxyFactory._creators
    assert "HttpLLM" not in OxyFactory._DANGEROUS_CLASSES
    assert "OpenAILLM" not in OxyFactory._DANGEROUS_CLASSES


def test_creators_initialized():
    """_init_creators should populate the mapping with all known classes."""
    assert len(OxyFactory._creators) >= 2
    for name in OxyFactory._creators:
        assert callable(OxyFactory._creators[name])
