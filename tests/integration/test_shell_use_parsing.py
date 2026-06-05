"""Integration tests for ShellUseAgent._parse_llm_response.

Tests cover: shell code block extraction, think tag handling, answer vs tool_call
state detection, error handling for malformed responses, and the send_email special case.
"""

import pytest

from oxygent.schemas import LLMState

try:
    from oxygent.oxy.agents.shell_use_agent import ShellUseAgent
except ImportError:
    pytest.skip("ShellUseAgent dependencies not available", allow_module_level=True)


@pytest.fixture
def shell_agent():
    """Create a ShellUseAgent for testing _parse_llm_response."""
    return ShellUseAgent(
        name="test_shell",
        desc="Test shell agent",
        llm_model="mock_llm",
    )


class TestShellCodeExtraction:
    def test_extracts_shell_code_block(self, shell_agent):
        response = "```shell\nls -la /tmp\n```"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == "ls -la /tmp"

    def test_extracts_first_shell_block_when_multiple(self, shell_agent):
        response = "```shell\nfirst_cmd\n```\nsome text\n```shell\nsecond_cmd\n```"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == "first_cmd"

    def test_multiline_shell_block(self, shell_agent):
        response = "```shell\ncd /home\nls -la\npwd\n```"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert "cd /home" in result.output
        assert "pwd" in result.output

    def test_shell_block_with_extra_newlines(self, shell_agent):
        response = "```\nshell\necho hello\n```"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.ori_response == response


class TestThinkTagHandling:
    def test_strips_think_tag(self, shell_agent):
        response = "<think>Let me think about this...</think>\n```shell\nwhoami\n```"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == "whoami"

    def test_strips_multiline_think_tag(self, shell_agent):
        response = (
            "<think>\nStep 1: Check user\nStep 2: Run cmd\n</think>\n```shell\nid\n```"
        )
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == "id"


class TestAnswerDetection:
    def test_python3_send_email_detected_as_answer_in_code_block(self, shell_agent):
        response = '```shell\npython3 send_email.py recipient@example.com "Hello"\n```'
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.ANSWER
        assert "python3 send_email.py" in result.output

    def test_python3_send_email_detected_as_answer_plain_text(self, shell_agent):
        response = 'python3 send_email.py user@test.com "Subject"'
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.ANSWER

    def test_non_send_email_plain_text_is_tool_call(self, shell_agent):
        response = "cat /etc/hosts"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == response


class TestNoShellBlock:
    def test_plain_text_without_code_block(self, shell_agent):
        response = "echo hello"
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == "echo hello"

    def test_code_block_with_wrong_language(self, shell_agent):
        response = '```python\nprint("hi")\n```'
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == response


class TestOriResponse:
    def test_ori_response_preserved(self, shell_agent):
        response = "Some explanation\n```shell\nuptime\n```\nDone."
        result = shell_agent._parse_llm_response(response)
        assert result.ori_response == response

    def test_ori_response_after_think_strip(self, shell_agent):
        response = "<think>blah</think>\n```shell\ndate\n```"
        result = shell_agent._parse_llm_response(response)
        assert "```shell" in result.ori_response
        assert "<think>" not in result.ori_response


class TestErrorHandling:
    def test_empty_response(self, shell_agent):
        response = ""
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
        assert result.output == ""

    def test_whitespace_only_response(self, shell_agent):
        response = "   \n  \n  "
        result = shell_agent._parse_llm_response(response)
        assert result.state is LLMState.TOOL_CALL
