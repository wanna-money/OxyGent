"""Integration tests for SkillAgent skill discovery.

Tests cover:
- SkillAgent discovers SKILL.md files from directories
- Skill metadata (name, description) parsed correctly from frontmatter
- Parent directory scanning for multiple skills
- Missing or empty skill directory handled gracefully
- Skill entries injected into _before_execute arguments
- SkillMetadata.from_frontmatter with kebab-case and snake_case keys

Shared fixtures from tests/conftest.py:
    reset_config, patch_config_defaults     (autouse)
    dummy_mas
"""

from pathlib import Path

import pytest

from oxygent.oxy.agents.skill_agent import (
    SkillAgent,
    _load_metadata_from_file,
    _parse_simple_frontmatter,
)
from oxygent.schemas.skill import SkillMetadata

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _patch_local_agent_config(monkeypatch):
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_agent_llm_model",
        lambda: "mock_llm",
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_agent_prompt",
        lambda: "You are a helpful assistant.",
    )
    monkeypatch.setattr(
        "oxygent.oxy.agents.local_agent.Config.get_vearch_config",
        lambda: None,
    )


def _write_skill_md(path: Path, name: str, description: str, **extra) -> Path:
    """Create a SKILL.md file at the given directory path."""
    path.mkdir(parents=True, exist_ok=True)
    skill_file = path / "SKILL.md"
    lines = ["---\n", f"name: {name}\n", f"description: {description}\n"]
    for key, value in extra.items():
        lines.append(f"{key}: {value}\n")
    lines.append("---\n")
    lines.append(f"\n# {name}\n\nSkill content here.\n")
    skill_file.write_text("".join(lines), encoding="utf-8")
    return skill_file


# ============================================================================
# Tests
# ============================================================================


class TestParseFrontmatter:
    """Test _parse_simple_frontmatter function."""

    def test_basic_key_value(self):
        lines = ["name: weather", "description: Get weather info"]
        result = _parse_simple_frontmatter(lines)
        assert result["name"] == "weather"
        assert result["description"] == "Get weather info"

    def test_quoted_values(self):
        lines = ['name: "my skill"', "description: 'A quoted desc'"]
        result = _parse_simple_frontmatter(lines)
        assert result["name"] == "my skill"
        assert result["description"] == "A quoted desc"

    def test_empty_lines_and_comments_skipped(self):
        lines = ["", "# This is a comment", "name: test", ""]
        result = _parse_simple_frontmatter(lines)
        assert result == {"name": "test"}

    def test_empty_input(self):
        result = _parse_simple_frontmatter([])
        assert result == {}


class TestLoadMetadataFromFile:
    """Test _load_metadata_from_file function."""

    def test_valid_skill_md(self, tmp_path):
        skill_file = _write_skill_md(tmp_path, "weather", "Get weather forecasts")
        metadata = _load_metadata_from_file(skill_file)

        assert metadata is not None
        assert metadata.name == "weather"
        assert metadata.description == "Get weather forecasts"
        assert metadata.skill_path == skill_file

    def test_missing_frontmatter_delimiters(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("No frontmatter here\n", encoding="utf-8")
        metadata = _load_metadata_from_file(skill_file)
        assert metadata is None

    def test_empty_frontmatter(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text("---\n---\nContent\n", encoding="utf-8")
        metadata = _load_metadata_from_file(skill_file)
        assert metadata is None

    def test_missing_required_field_name(self, tmp_path):
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(
            "---\ndescription: no name field\n---\n",
            encoding="utf-8",
        )
        metadata = _load_metadata_from_file(skill_file)
        assert metadata is None

    def test_nonexistent_file(self, tmp_path):
        fake_path = tmp_path / "nonexistent" / "SKILL.md"
        metadata = _load_metadata_from_file(fake_path)
        assert metadata is None

    def test_skill_with_extra_fields(self, tmp_path):
        skill_file = _write_skill_md(
            tmp_path, "coder", "Code generation", version="1.0.0", author="Test Author"
        )
        metadata = _load_metadata_from_file(skill_file)

        assert metadata is not None
        assert metadata.name == "coder"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"


class TestSkillMetadataFromFrontmatter:
    """Test SkillMetadata.from_frontmatter."""

    def test_basic_creation(self, tmp_path):
        frontmatter = {"name": "test", "description": "Test skill"}
        skill_path = tmp_path / "SKILL.md"
        metadata = SkillMetadata.from_frontmatter(frontmatter, skill_path)

        assert metadata.name == "test"
        assert metadata.description == "Test skill"
        assert metadata.skill_path == skill_path

    def test_missing_name_raises(self, tmp_path):
        frontmatter = {"description": "No name"}
        with pytest.raises(ValueError, match="name"):
            SkillMetadata.from_frontmatter(frontmatter, tmp_path / "SKILL.md")

    def test_missing_description_raises(self, tmp_path):
        frontmatter = {"name": "test"}
        with pytest.raises(ValueError, match="description"):
            SkillMetadata.from_frontmatter(frontmatter, tmp_path / "SKILL.md")

    def test_kebab_case_keys(self, tmp_path):
        frontmatter = {
            "name": "test",
            "description": "Test",
            "disable-model-invocation": "true",
            "user-invocable": "true",
            "argument-hint": "Provide a query",
        }
        metadata = SkillMetadata.from_frontmatter(frontmatter, tmp_path / "SKILL.md")

        assert metadata.disable_model_invocation is True
        assert metadata.user_invocable is True
        assert metadata.argument_hint == "Provide a query"

    def test_snake_case_keys(self, tmp_path):
        frontmatter = {
            "name": "test",
            "description": "Test",
            "disable_model_invocation": True,
            "user_invocable": True,
            "argument_hint": "Some hint",
        }
        metadata = SkillMetadata.from_frontmatter(frontmatter, tmp_path / "SKILL.md")

        assert metadata.disable_model_invocation is True
        assert metadata.user_invocable is True
        assert metadata.argument_hint == "Some hint"


class TestSkillAgentDiscovery:
    """Test SkillAgent discovers skills from directories."""

    @pytest.mark.asyncio
    async def test_discover_single_skill(self, monkeypatch, dummy_mas, tmp_path):
        """SkillAgent should discover a single skill from a direct path."""
        _patch_local_agent_config(monkeypatch)

        from oxygent.oxy.llms.mock_llm import MockLLM

        llm = MockLLM(name="mock_llm", func_mock_process=lambda r: "response")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        skill_dir = tmp_path / "weather_skill"
        _write_skill_md(skill_dir, "weather", "Get weather forecasts")

        agent = SkillAgent(
            name="skill_agent",
            desc="Skill-aware agent",
            llm_model="mock_llm",
            skills=[str(skill_dir)],
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        assert agent.skills_count == 1
        assert "weather" in agent.skill_names

    @pytest.mark.asyncio
    async def test_discover_multiple_skills_from_parent(
        self, monkeypatch, dummy_mas, tmp_path
    ):
        """SkillAgent should discover multiple skills from a parent directory."""
        _patch_local_agent_config(monkeypatch)

        from oxygent.oxy.llms.mock_llm import MockLLM

        llm = MockLLM(name="mock_llm", func_mock_process=lambda r: "response")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        parent_dir = tmp_path / "skills"
        _write_skill_md(parent_dir / "weather", "weather", "Weather info")
        _write_skill_md(parent_dir / "coder", "coder", "Code generation")
        _write_skill_md(parent_dir / "math", "math", "Math calculations")

        agent = SkillAgent(
            name="skill_agent",
            desc="Skill-aware agent",
            llm_model="mock_llm",
            skills=[str(parent_dir)],
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        assert agent.skills_count == 3
        assert sorted(agent.skill_names) == ["coder", "math", "weather"]

    @pytest.mark.asyncio
    async def test_nonexistent_path_handled_gracefully(
        self, monkeypatch, dummy_mas, tmp_path
    ):
        """SkillAgent should handle nonexistent skill paths gracefully."""
        _patch_local_agent_config(monkeypatch)

        from oxygent.oxy.llms.mock_llm import MockLLM

        llm = MockLLM(name="mock_llm", func_mock_process=lambda r: "response")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        agent = SkillAgent(
            name="skill_agent",
            desc="Skill-aware agent",
            llm_model="mock_llm",
            skills=[str(tmp_path / "nonexistent")],
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        assert agent.skills_count == 0

    @pytest.mark.asyncio
    async def test_no_skills_configured(self, monkeypatch, dummy_mas):
        """SkillAgent with skills=None should initialize with zero skills."""
        _patch_local_agent_config(monkeypatch)

        from oxygent.oxy.llms.mock_llm import MockLLM

        llm = MockLLM(name="mock_llm", func_mock_process=lambda r: "response")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        agent = SkillAgent(
            name="skill_agent",
            desc="Skill-aware agent",
            llm_model="mock_llm",
            skills=None,
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        assert agent.skills_count == 0

    @pytest.mark.asyncio
    async def test_skill_entries_injected_into_arguments(
        self, monkeypatch, dummy_mas, tmp_path
    ):
        """After _before_execute, skill_list should be in arguments."""
        _patch_local_agent_config(monkeypatch)

        from oxygent.oxy.llms.mock_llm import MockLLM
        from oxygent.schemas import OxyRequest

        llm = MockLLM(name="mock_llm", func_mock_process=lambda r: "response")
        llm.set_mas(dummy_mas)
        dummy_mas.add_oxy(llm)

        skill_dir = tmp_path / "my_skill"
        _write_skill_md(skill_dir, "my_skill", "Does something useful")

        agent = SkillAgent(
            name="skill_agent",
            desc="Skill-aware agent",
            llm_model="mock_llm",
            skills=[str(skill_dir)],
        )
        agent.set_mas(dummy_mas)
        dummy_mas.add_oxy(agent)
        await agent.init()

        oxy_request = OxyRequest(
            arguments={"query": "test"},
            caller="user",
            caller_category="user",
        )
        oxy_request.set_mas(dummy_mas)

        result_request = await agent._before_execute(oxy_request)

        assert "skill_list" in result_request.arguments
        assert "my_skill" in result_request.arguments["skill_list"]
        assert "Does something useful" in result_request.arguments["skill_list"]
