"""Integration tests for conversation memory management.

Tests cover:
- Memory sliding window truncation via Memory.to_dict_list()
- System message preservation after truncation
- Memory accumulation in multi-turn conversations
- Message factory constructors

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
"""

import pytest

from oxygent.schemas.memory import Memory, Message

# ============================================================================
# Tests
# ============================================================================


class TestMemorySlidingWindow:
    """Test Memory's sliding-window truncation behavior."""

    def test_to_dict_list_no_truncation(self):
        """When message count is below the threshold, all messages are kept."""
        mem = Memory(max_messages=50)
        mem.add_message(Message.system_message("System prompt"))
        mem.add_message(Message.user_message("Hello"))
        mem.add_message(Message.assistant_message("Hi there!"))

        result = mem.to_dict_list()
        assert len(result) == 3
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
        assert result[2]["role"] == "assistant"

    def test_to_dict_list_truncation_preserves_system(self):
        """When messages exceed the threshold, truncation keeps the system
        message at the front and the most recent messages."""
        mem = Memory(max_messages=50)
        mem.add_message(Message.system_message("System prompt"))

        for i in range(30):
            mem.add_message(Message.user_message(f"User message {i}"))
            mem.add_message(Message.assistant_message(f"Assistant reply {i}"))

        result = mem.to_dict_list(short_memory_size=5)

        assert result[0]["role"] == "system"
        assert result[0]["content"] == "System prompt"

        # short_memory_size=5 means we keep 5*2+1=11 recent messages + system = 12
        assert len(result) == 12

    def test_to_dict_list_truncation_without_system(self):
        """Truncation when the first message is not a system message."""
        mem = Memory(max_messages=50)

        for i in range(20):
            mem.add_message(Message.user_message(f"User {i}"))
            mem.add_message(Message.assistant_message(f"Reply {i}"))

        result = mem.to_dict_list(short_memory_size=3)

        # 3*2+1=7 recent messages
        assert len(result) == 7
        assert result[0]["role"] in ("user", "assistant")

    def test_to_dict_list_with_explicit_short_memory_size(self):
        """Explicit short_memory_size controls the truncation window."""
        mem = Memory(max_messages=50)
        mem.add_message(Message.system_message("Prompt"))

        for i in range(50):
            mem.add_message(Message.user_message(f"msg {i}"))
            mem.add_message(Message.assistant_message(f"reply {i}"))

        result_small = mem.to_dict_list(short_memory_size=2)
        result_large = mem.to_dict_list(short_memory_size=10)

        assert len(result_small) < len(result_large)


class TestMemoryOperations:
    """Test Memory add/clear/get operations."""

    def test_add_message(self):
        mem = Memory()
        msg = Message.user_message("Hello")
        mem.add_message(msg)
        assert len(mem.messages) == 1
        assert mem.messages[0].content == "Hello"

    def test_add_messages_batch(self):
        mem = Memory()
        msgs = [
            Message.user_message("A"),
            Message.assistant_message("B"),
            Message.user_message("C"),
        ]
        mem.add_messages(msgs)
        assert len(mem.messages) == 3

    def test_clear(self):
        mem = Memory()
        mem.add_message(Message.user_message("Hello"))
        mem.add_message(Message.assistant_message("World"))
        mem.clear()
        assert len(mem.messages) == 0

    def test_get_recent_messages(self):
        mem = Memory()
        for i in range(10):
            mem.add_message(Message.user_message(f"msg_{i}"))

        recent = mem.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[0].content == "msg_7"
        assert recent[2].content == "msg_9"


class TestMessageFactories:
    """Test Message factory constructors."""

    def test_user_message(self):
        msg = Message.user_message("Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_system_message(self):
        msg = Message.system_message("System prompt")
        assert msg.role == "system"
        assert msg.content == "System prompt"

    def test_assistant_message(self):
        msg = Message.assistant_message("Reply")
        assert msg.role == "assistant"
        assert msg.content == "Reply"

    def test_assistant_message_no_content(self):
        msg = Message.assistant_message()
        assert msg.role == "assistant"
        assert msg.content is None

    def test_tool_message(self):
        msg = Message.tool_message(
            content="result", name="calculator", tool_call_id="call_123"
        )
        assert msg.role == "tool"
        assert msg.content == "result"
        assert msg.name == "calculator"
        assert msg.tool_call_id == "call_123"

    def test_to_dict(self):
        msg = Message.user_message("Hello world")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "Hello world"}

    def test_to_dict_with_tool_calls(self):
        from oxygent.schemas.memory import Function, ToolCall

        tc = ToolCall(
            id="call_1",
            type="function",
            function=Function(name="calc", arguments='{"x": 1}'),
        )
        msg = Message(role="assistant", tool_calls=[tc])
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert len(d["tool_calls"]) == 1
        assert d["tool_calls"][0]["function"]["name"] == "calc"


class TestMessageComposition:
    """Test Message __add__ and __radd__ for list composition."""

    def test_message_plus_list(self):
        msg = Message.user_message("A")
        result = msg + [Message.assistant_message("B")]
        assert len(result) == 2
        assert result[0].content == "A"
        assert result[1].content == "B"

    def test_list_plus_message(self):
        result = [Message.user_message("A")] + Message.assistant_message("B")
        assert len(result) == 2

    def test_message_plus_message(self):
        a = Message.user_message("A")
        b = Message.assistant_message("B")
        result = a + b
        assert len(result) == 2

    def test_message_plus_invalid_raises(self):
        msg = Message.user_message("A")
        with pytest.raises(TypeError):
            msg + 42


class TestDictListToMessages:
    """Test Message.dict_list_to_messages reverse conversion."""

    def test_round_trip(self):
        original = [
            Message.system_message("sys"),
            Message.user_message("hello"),
            Message.assistant_message("hi"),
        ]
        dict_list = [m.to_dict() for m in original]
        restored = Message.dict_list_to_messages(dict_list)

        assert len(restored) == 3
        assert restored[0].role == "system"
        assert restored[0].content == "sys"
        assert restored[1].role == "user"
        assert restored[2].role == "assistant"
