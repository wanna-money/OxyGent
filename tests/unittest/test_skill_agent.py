"""Unit tests for skill_agent utility functions and SkillMetadata."""

from pathlib import Path

import pytest

from oxygent.oxy.agents.skill_agent import (
    _load_metadata_from_file,
    _parse_simple_frontmatter,
)
from oxygent.schemas.skill import SkillMetadata


# ──────────────────────────────────────────────────────────────────────────────
# _parse_simple_frontmatter
# ──────────────────────────────────────────────────────────────────────────────
def test_parse_frontmatter_basic():
    lines = ["name: my_skill", "description: A useful skill"]
    result = _parse_simple_frontmatter(lines)
    assert result == {"name": "my_skill", "description": "A useful skill"}


def test_parse_frontmatter_strips_whitespace():
    lines = ["  name :  my_skill  ", "  description :  A skill  "]
    result = _parse_simple_frontmatter(lines)
    assert result["name"] == "my_skill"
    assert result["description"] == "A skill"


def test_parse_frontmatter_skips_empty_and_comments():
    lines = ["", "# This is a comment", "name: test", "", "version: 1.0"]
    result = _parse_simple_frontmatter(lines)
    assert result == {"name": "test", "version": "1.0"}


def test_parse_frontmatter_removes_quotes():
    lines = ['name: "quoted"', "description: 'single_quoted'"]
    result = _parse_simple_frontmatter(lines)
    assert result["name"] == "quoted"
    assert result["description"] == "single_quoted"


def test_parse_frontmatter_no_colon():
    lines = ["no_colon_line", "name: valid"]
    result = _parse_simple_frontmatter(lines)
    assert "no_colon_line" not in result
    assert result["name"] == "valid"


def test_parse_frontmatter_empty():
    assert _parse_simple_frontmatter([]) == {}


def test_parse_frontmatter_colon_in_value():
    lines = ["url: http://example.com:8080"]
    result = _parse_simple_frontmatter(lines)
    assert result["url"] == "http://example.com:8080"


# ──────────────────────────────────────────────────────────────────────────────
# _load_metadata_from_file
# ──────────────────────────────────────────────────────────────────────────────
def test_load_metadata_valid(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\nname: weather\ndescription: Get weather info\nversion: 1.0\n---\n\n# Weather Skill\n..."
    )
    result = _load_metadata_from_file(skill_md)
    assert result is not None
    assert isinstance(result, SkillMetadata)
    assert result.name == "weather"
    assert result.description == "Get weather info"
    assert result.version == "1.0"
    assert result.skill_path == skill_md


def test_load_metadata_missing_frontmatter_delim(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("No frontmatter here\nJust text.")
    result = _load_metadata_from_file(skill_md)
    assert result is None


def test_load_metadata_empty_file(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("")
    result = _load_metadata_from_file(skill_md)
    assert result is None


def test_load_metadata_no_closing_delim(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: test\ndescription: test\n")
    result = _load_metadata_from_file(skill_md)
    assert result is None


def test_load_metadata_missing_name(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\ndescription: only description\n---\n")
    result = _load_metadata_from_file(skill_md)
    assert result is None


def test_load_metadata_missing_description(tmp_path):
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: only_name\n---\n")
    result = _load_metadata_from_file(skill_md)
    assert result is None


def test_load_metadata_nonexistent_file():
    result = _load_metadata_from_file(Path("/nonexistent/SKILL.md"))
    assert result is None


# ──────────────────────────────────────────────────────────────────────────────
# SkillMetadata.from_frontmatter
# ──────────────────────────────────────────────────────────────────────────────
def test_from_frontmatter_basic(tmp_path):
    meta = SkillMetadata.from_frontmatter(
        {"name": "test", "description": "A test skill"},
        tmp_path / "SKILL.md",
    )
    assert meta.name == "test"
    assert meta.description == "A test skill"


def test_from_frontmatter_missing_name(tmp_path):
    with pytest.raises(ValueError, match="name"):
        SkillMetadata.from_frontmatter(
            {"description": "only desc"},
            tmp_path / "SKILL.md",
        )


def test_from_frontmatter_missing_description(tmp_path):
    with pytest.raises(ValueError, match="description"):
        SkillMetadata.from_frontmatter(
            {"name": "only_name"},
            tmp_path / "SKILL.md",
        )


def test_from_frontmatter_optional_fields(tmp_path):
    meta = SkillMetadata.from_frontmatter(
        {
            "name": "test",
            "description": "desc",
            "version": "2.0",
            "author": "Alice",
            "disable-model-invocation": "true",
            "user-invocable": "",
            "argument-hint": "provide a city name",
        },
        tmp_path / "SKILL.md",
    )
    assert meta.version == "2.0"
    assert meta.author == "Alice"
    assert meta.disable_model_invocation is True
    assert meta.user_invocable is False
    assert meta.argument_hint == "provide a city name"
