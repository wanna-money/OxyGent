"""Integration tests for file_tools FunctionHub.

Tests cover: write_file, read_file, delete_file, view_text_file,
and path security checks that prevent escaping the allowed directory.
"""

import os
import sys

import pytest

from oxygent.preset_tools.file_tools import (
    _read_file_with_range,
    delete_file,
    read_file,
    view_text_file,
    write_file,
)

_ft_module = sys.modules["oxygent.preset_tools.file_tools"]


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Create a temp directory and patch allowed_dir to it."""
    monkeypatch.setattr(_ft_module, "allowed_dir", str(tmp_path))
    return tmp_path


class TestWriteFile:
    @pytest.mark.asyncio
    async def test_write_creates_new_file(self, sandbox):
        path = str(sandbox / "new.txt")
        result = await write_file(path=path, content="hello")
        assert "Successfully wrote" in result
        assert os.path.exists(path)
        with open(path) as f:
            assert f.read() == "hello"

    @pytest.mark.asyncio
    async def test_write_overwrites_existing_file(self, sandbox):
        path = str(sandbox / "overwrite.txt")
        await write_file(path=path, content="first")
        await write_file(path=path, content="second")
        with open(path) as f:
            assert f.read() == "second"

    @pytest.mark.asyncio
    async def test_write_unicode_content(self, sandbox):
        path = str(sandbox / "unicode.txt")
        content = "你好世界 🌍"
        await write_file(path=path, content=content)
        with open(path, encoding="utf-8") as f:
            assert f.read() == content

    @pytest.mark.asyncio
    async def test_write_outside_allowed_dir_raises(self, sandbox):
        with pytest.raises(ValueError, match="outside"):
            await write_file(path="/tmp/evil.txt", content="hack")


class TestReadFile:
    @pytest.mark.asyncio
    async def test_read_existing_file(self, sandbox):
        path = str(sandbox / "read_me.txt")
        with open(path, "w") as f:
            f.write("content here")
        result = await read_file(path=path)
        assert result == "content here"

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, sandbox):
        path = str(sandbox / "nope.txt")
        result = await read_file(path=path)
        assert "does not exist" in result

    @pytest.mark.asyncio
    async def test_read_outside_allowed_dir_raises(self, sandbox):
        with pytest.raises(ValueError, match="outside"):
            await read_file(path="/etc/passwd")


class TestDeleteFile:
    @pytest.mark.asyncio
    async def test_delete_existing_file(self, sandbox):
        path = str(sandbox / "to_delete.txt")
        with open(path, "w") as f:
            f.write("bye")
        result = await delete_file(path=path)
        assert "Successfully deleted the file" in result
        assert not os.path.exists(path)

    @pytest.mark.asyncio
    async def test_delete_existing_directory(self, sandbox):
        dir_path = sandbox / "subdir"
        dir_path.mkdir()
        (dir_path / "child.txt").write_text("x")
        result = await delete_file(path=str(dir_path))
        assert "Successfully deleted the directory" in result
        assert not os.path.exists(str(dir_path))

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, sandbox):
        path = str(sandbox / "ghost.txt")
        result = await delete_file(path=path)
        assert "does not exist" in result

    @pytest.mark.asyncio
    async def test_delete_outside_allowed_dir_raises(self, sandbox):
        with pytest.raises(ValueError, match="outside"):
            await delete_file(path="/tmp/evil.txt")


class TestViewTextFile:
    @pytest.mark.asyncio
    async def test_view_full_file(self, sandbox):
        path = str(sandbox / "lines.txt")
        with open(path, "w") as f:
            f.write("line1\nline2\nline3\n")
        result = await view_text_file(file_path=path)
        assert "1 | line1" in result
        assert "2 | line2" in result
        assert "3 | line3" in result

    @pytest.mark.asyncio
    async def test_view_with_range(self, sandbox):
        path = str(sandbox / "range.txt")
        lines = [f"line{i}\n" for i in range(1, 11)]
        with open(path, "w") as f:
            f.writelines(lines)
        result = await view_text_file(file_path=path, ranges=[3, 5])
        assert "3 | line3" in result
        assert "5 | line5" in result
        assert "2 | line2" not in result
        assert "6 | line6" not in result

    @pytest.mark.asyncio
    async def test_view_negative_range(self, sandbox):
        path = str(sandbox / "neg_range.txt")
        lines = [f"line{i}\n" for i in range(1, 6)]
        with open(path, "w") as f:
            f.writelines(lines)
        result = await view_text_file(file_path=path, ranges=[-2, -1])
        assert "4 | line4" in result
        assert "5 | line5" in result

    @pytest.mark.asyncio
    async def test_view_nonexistent_file(self, sandbox):
        result = await view_text_file(file_path=str(sandbox / "nope.txt"))
        assert "does not exist" in result

    @pytest.mark.asyncio
    async def test_view_not_a_file(self, sandbox):
        dir_path = sandbox / "adir"
        dir_path.mkdir()
        result = await view_text_file(file_path=str(dir_path))
        assert "not a file" in result

    @pytest.mark.asyncio
    async def test_view_invalid_range(self, sandbox):
        path = str(sandbox / "invalid.txt")
        with open(path, "w") as f:
            f.write("line1\n")
        result = await view_text_file(file_path=path, ranges=[5, 1])
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_view_outside_allowed_dir_raises(self, sandbox):
        with pytest.raises(ValueError, match="outside"):
            await view_text_file(file_path="/etc/passwd")


class TestReadFileWithRange:
    def test_full_read(self, sandbox):
        path = str(sandbox / "full.txt")
        with open(path, "w") as f:
            f.write("a\nb\nc\n")
        result = _read_file_with_range(path, None)
        assert "1 | a" in result
        assert "3 | c" in result

    def test_invalid_range_length(self, sandbox):
        path = str(sandbox / "x.txt")
        with open(path, "w") as f:
            f.write("x\n")
        with pytest.raises(ValueError, match="two integers"):
            _read_file_with_range(path, [1, 2, 3])

    def test_start_greater_than_end(self, sandbox):
        path = str(sandbox / "y.txt")
        with open(path, "w") as f:
            f.write("a\nb\nc\n")
        with pytest.raises(ValueError, match="Invalid range"):
            _read_file_with_range(path, [3, 1])

    def test_clamping_out_of_bounds(self, sandbox):
        path = str(sandbox / "clamp.txt")
        with open(path, "w") as f:
            f.write("a\nb\n")
        result = _read_file_with_range(path, [1, 100])
        assert "1 | a" in result
        assert "2 | b" in result
