"""Integration tests for SSE utility functions (oxygent/utils/sse_utils.py).

Tests cover: basic event parsing, multi-field events, comment handling,
buffer overflow protection, per-event size limit, data size limit,
NUL-in-id rejection, retry field parsing, partial final event flush,
CR/LF normalization, and empty-field handling.
"""

import pytest

from oxygent.utils.sse_utils import iter_sse_events

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeContent:
    """Simulates aiohttp response.content with iter_chunked()."""

    def __init__(self, chunks: list[bytes]):
        self._chunks = chunks

    async def iter_chunked(self, chunk_size: int):
        for chunk in self._chunks:
            yield chunk


class FakeResponse:
    """Simulates aiohttp.ClientResponse."""

    def __init__(self, chunks: list[bytes]):
        self.content = FakeContent(chunks)


async def collect_events(resp, **kwargs) -> list[dict]:
    events = []
    async for evt in iter_sse_events(resp, **kwargs):
        events.append(evt)
    return events


# ---------------------------------------------------------------------------
# Tests: Basic parsing
# ---------------------------------------------------------------------------


class TestBasicParsing:
    @pytest.mark.asyncio
    async def test_single_data_event(self):
        raw = b"data: hello world\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) == 1
        assert events[0]["data"] == "hello world"
        assert events[0]["event"] is None

    @pytest.mark.asyncio
    async def test_multiple_events(self):
        raw = b"data: first\n\ndata: second\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) == 2
        assert events[0]["data"] == "first"
        assert events[1]["data"] == "second"

    @pytest.mark.asyncio
    async def test_multiline_data(self):
        raw = b"data: line1\ndata: line2\ndata: line3\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) == 1
        assert events[0]["data"] == "line1\nline2\nline3"

    @pytest.mark.asyncio
    async def test_event_type_field(self):
        raw = b"event: custom\ndata: payload\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["event"] == "custom"
        assert events[0]["data"] == "payload"

    @pytest.mark.asyncio
    async def test_id_field(self):
        raw = b"id: 42\ndata: msg\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["id"] == "42"

    @pytest.mark.asyncio
    async def test_retry_field_valid(self):
        raw = b"retry: 5000\ndata: reconnect\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["retry"] == 5000

    @pytest.mark.asyncio
    async def test_retry_field_negative_ignored(self):
        raw = b"retry: -1\ndata: ignore\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["retry"] is None

    @pytest.mark.asyncio
    async def test_retry_field_non_numeric_ignored(self):
        raw = b"retry: abc\ndata: ignore\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["retry"] is None


# ---------------------------------------------------------------------------
# Tests: Comment and empty-field handling
# ---------------------------------------------------------------------------


class TestComments:
    @pytest.mark.asyncio
    async def test_comment_lines_ignored(self):
        raw = b": this is a comment\ndata: real\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) == 1
        assert events[0]["data"] == "real"

    @pytest.mark.asyncio
    async def test_heartbeat_comment_only_skipped(self):
        raw = b": heartbeat\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_empty_field_name_ignored(self):
        raw = b":value\ndata: keep\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["data"] == "keep"


# ---------------------------------------------------------------------------
# Tests: Security hardening
# ---------------------------------------------------------------------------


class TestSecurityLimits:
    @pytest.mark.asyncio
    async def test_buffer_overflow_raises(self):
        huge_chunk = b"x" * (3 * 1024 * 1024)
        with pytest.raises(ValueError, match="buffer too large"):
            await collect_events(FakeResponse([huge_chunk]))

    @pytest.mark.asyncio
    async def test_event_too_large_raises(self):
        big_event = b"data: " + b"x" * (600 * 1024) + b"\n\n"
        with pytest.raises(ValueError, match="event too large"):
            await collect_events(FakeResponse([big_event]))

    @pytest.mark.asyncio
    async def test_data_too_large_raises(self):
        lines = []
        for _ in range(600):
            lines.append(b"data: " + b"x" * 1024 + b"\n")
        lines.append(b"\n")
        with pytest.raises(ValueError, match="too large"):
            await collect_events(FakeResponse([b"".join(lines)]))

    @pytest.mark.asyncio
    async def test_id_with_nul_ignored(self):
        raw = b"id: bad\x00id\ndata: msg\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["id"] is None
        assert events[0]["data"] == "msg"


# ---------------------------------------------------------------------------
# Tests: Chunked delivery and CR/LF normalization
# ---------------------------------------------------------------------------


class TestChunking:
    @pytest.mark.asyncio
    async def test_event_split_across_chunks(self):
        chunk1 = b"data: hel"
        chunk2 = b"lo\n\n"
        events = await collect_events(FakeResponse([chunk1, chunk2]))
        assert events[0]["data"] == "hello"

    @pytest.mark.asyncio
    async def test_crlf_normalization(self):
        raw = b"data: crlf\r\n\r\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) == 1
        assert events[0]["data"] == "crlf"

    @pytest.mark.asyncio
    async def test_bare_cr_normalization(self):
        raw = b"data: cr\r\rdata: next\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert len(events) >= 1

    @pytest.mark.asyncio
    async def test_cr_at_chunk_boundary(self):
        chunk1 = b"data: split\r"
        chunk2 = b"\ndata: more\n\n"
        events = await collect_events(FakeResponse([chunk1, chunk2]))
        assert any("split" in evt["data"] for evt in events)


# ---------------------------------------------------------------------------
# Tests: Partial final event
# ---------------------------------------------------------------------------


class TestPartialFinalEvent:
    @pytest.mark.asyncio
    async def test_partial_event_flushed_on_eof(self):
        raw = b"data: no trailing double newline"
        events = await collect_events(
            FakeResponse([raw]), allow_partial_final_event=True
        )
        assert len(events) == 1
        assert events[0]["data"] == "no trailing double newline"

    @pytest.mark.asyncio
    async def test_partial_event_not_flushed_when_disabled(self):
        raw = b"data: no trailing double newline"
        events = await collect_events(
            FakeResponse([raw]), allow_partial_final_event=False
        )
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_empty_buffer_at_eof(self):
        raw = b"data: complete\n\n"
        events = await collect_events(
            FakeResponse([raw]), allow_partial_final_event=True
        )
        assert len(events) == 1


# ---------------------------------------------------------------------------
# Tests: Field parsing edge cases
# ---------------------------------------------------------------------------


class TestFieldEdgeCases:
    @pytest.mark.asyncio
    async def test_data_with_colon_in_value(self):
        raw = b"data: key: value: more\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["data"] == "key: value: more"

    @pytest.mark.asyncio
    async def test_field_with_no_value(self):
        raw = b"data\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["data"] == ""

    @pytest.mark.asyncio
    async def test_data_with_leading_space_stripped(self):
        raw = b"data:  two spaces\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["data"] == " two spaces"

    @pytest.mark.asyncio
    async def test_empty_data_line(self):
        raw = b"data:\n\n"
        events = await collect_events(FakeResponse([raw]))
        assert events[0]["data"] == ""
