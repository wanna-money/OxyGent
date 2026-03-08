#!/usr/bin/env python3
"""
SkillAgent: Lightweight skill-aware agent with direct path-based skill loading.

This module provides a simplified skill-aware agent that loads skills directly
from specified paths without requiring global registry or SkillSource components.

Core Design:
    1. Accepts skill paths directly via `skills` parameter (path strings)
    2. Discovers and loads skills from paths during initialization
    3. Enhances system prompt with discovered skill metadata

Usage:
    >>> oxy_space = [
    ...     oxy.SkillAgent(
    ...         name="agent",
    ...         skills=["./skills/weather", "./skills/code"]  # Direct paths
    ...     ),
    ... ]

Attributes:
    skills: List of skill directory paths to load skills from.
    skill_prompt_template: Template for generating skill prompt section.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import Field

from oxygent.schemas.skill_metadata import SkillMetadata
from .react_agent import ReActAgent

logger = logging.getLogger(__name__)


def _parse_simple_frontmatter(lines: List[str]) -> Dict[str, str]:
    """Parse simple key-value frontmatter (no nested structures).

    Supports basic 'key: value' format only.

    Args:
        lines: List of frontmatter lines.

    Returns:
        Dictionary of key-value pairs.
    """
    result = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            result[key] = value
    return result


def _load_metadata_from_file(skill_path: Path) -> Optional[SkillMetadata]:
    """Load metadata from a SKILL.md file.

    Parses the frontmatter to extract name and description.
    Does not read the full markdown body to minimize I/O.

    Args:
        skill_path: Path to the SKILL.md file.

    Returns:
        SkillMetadata if successful, None otherwise.
    """
    try:
        with skill_path.open(encoding="utf-8") as handle:
            first_line = handle.readline()
            if not first_line or first_line.strip() != "---":
                logger.warning(f"SKILL.md missing frontmatter: {skill_path}")
                return None

            frontmatter_lines = []
            for line in handle:
                if line.strip() == "---":
                    break
                frontmatter_lines.append(line)
            else:
                logger.warning(f"Invalid SKILL.md frontmatter format: {skill_path}")
                return None

        frontmatter = _parse_simple_frontmatter(frontmatter_lines)

        if not frontmatter:
            logger.warning(f"Empty frontmatter in: {skill_path}")
            return None

        return SkillMetadata.from_frontmatter(frontmatter, skill_path)

    except Exception as e:
        logger.warning(f"Failed to load skill metadata from {skill_path}: {e}")
        return None


class SkillAgent(ReActAgent):
    """Lightweight skill-aware agent with direct path-based skill loading.

    A simplified agent that loads skills directly from specified directory paths
    without requiring global registry or SkillSource components.

    This agent does NOT provide:
        - Skill activation (manual or automatic)
        - Skill selection via LLM
        - Runtime skill content loading

    Architecture:
        1. Configuration: skills=["./path/to/skill1", "./path/to/skill2"]
        2. Initialization: Discovers skills from each path
        3. Prompt Enhancement: Injects skill metadata into system prompt

    Attributes:
        skills: List of skill directory paths to load skills from.
            Each path should point to a directory containing SKILL.md file,
            or a parent directory containing multiple skill subdirectories.
        skill_prompt_template: Jinja-like template for skill prompt section.
            Use {skill_list} placeholder for skill entries.
        _skills_metadata: Internal cache of discovered skill metadata.
            Maps skill name -> SkillMetadata.

    Example:
        >>> agent = SkillAgent(
        ...     name="assistant",
        ...     skills=["./skills/project", "./skills/code"]
        ... )
        >>> # Agent will discover skills from both paths
    """

    skills: Optional[List[str]] = Field(
        default=None,
        description="List of skill directory paths to load skills from. "
                    "Each path can be a skill folder with SKILL.md or a parent "
                    "directory containing multiple skill subfolders.",
    )

    skill_prompt_template: str = Field(
        default="""# IMPORTANT
- Don't make any assumptions. All your knowledge about available capabilities must come from your equipped skills.
- If the current information is sufficient to answer the question, do NOT invoke any tools or skills.
- Only use skills when you need specialized knowledge, workflows, or resources that are not in your current context.

# Agent Skills
The agent skills are a collection of instructions, scripts, and resources that you can load dynamically to improve performance on specialized tasks. Each agent skill has a `SKILL.md` file in its folder that describes how to use the skill. If you want to use a skill, you MUST read its `SKILL.md` file carefully.

{skill_list}

---
""",
        description="Template for generating skill prompt section. "
                    "Use {skill_list} as placeholder for skill entries.",
    )

    # Internal state (private attributes, not Pydantic fields)
    _skills_metadata: Dict[str, SkillMetadata] = {}

    @property
    def skills_count(self) -> int:
        """Number of discovered skills.

        Returns:
            Count of unique skills discovered from all paths.
        """
        return len(self._skills_metadata)

    @property
    def skill_names(self) -> List[str]:
        """Names of all discovered skills.

        Returns:
            Sorted list of skill names available to this agent.
        """
        return sorted(self._skills_metadata.keys())

    async def init(self) -> None:
        """Initialize the agent with skill discovery.

        Initialization sequence:
            1. Discover skills from each specified path
            2. Load skill metadata (name, description, argument_hint)
            3. Build skill prompt section
            4. Inject skill prompt into additional_prompt
            5. Call parent init

        Logs:
            - INFO: Initialization start and completion
            - DEBUG: Per-path skill discovery
            - WARNING: Invalid paths or missing skills
            - ERROR: Failed path initializations
        """
        logger.info(
            f"[SkillAgent] Initializing agent '{self.name}' "
            f"with {len(self.skills) if self.skills else 0} skill path(s)"
        )

        # Phase 1: Discover and load skills
        await self._discover_skills()

        # Phase 2: Build skill prompt and enhance system prompt
        await self._build_skill_prompt()

        # Phase 3: Call parent init
        await super().init()

        logger.info(
            f"[SkillAgent] Agent '{self.name}' initialized: "
            f"{self.skills_count} skills discovered and ready"
        )

    async def _discover_skills(self) -> None:
        """Discover and load skill metadata directly from paths.

        This method scans each path for SKILL.md files and loads
        skill metadata directly, without using global registry.

        Process:
            1. For each path, resolve to absolute path
            2. If path contains SKILL.md, load it as single skill
            3. If path is directory, search for SKILL.md files (recursive)
            4. Collect metadata into _skills_metadata

        Raises:
            No exceptions raised; errors are logged and skipped.

        Note:
            Skills with duplicate names from different paths will be
            overwritten by the last path's version.
        """
        if not self.skills:
            logger.debug(
                f"[SkillAgent] Agent '{self.name}': "
                f"No skill paths configured"
            )
            return

        logger.debug(
            f"[SkillAgent] Agent '{self.name}': "
            f"Discovering skills from {len(self.skills)} path(s)"
        )

        successful_paths = 0
        failed_paths = 0

        for skill_path_str in self.skills:
            try:
                skill_path = Path(skill_path_str).expanduser()

                # Convert relative path to absolute path
                if not skill_path.is_absolute():
                    skill_path = Path.cwd() / skill_path

                if not skill_path.exists():
                    logger.warning(
                        f"[SkillAgent] Agent '{self.name}': "
                        f"Path does not exist: {skill_path}"
                    )
                    failed_paths += 1
                    continue

                # Non-skill subdirectories to skip
                non_skill_subdirs = {"scripts", "references", "assets"}

                # Check if this is a direct skill folder (contains SKILL.md)
                if (skill_path / "SKILL.md").exists():
                    skill_file = skill_path / "SKILL.md"
                    metadata = _load_metadata_from_file(skill_file)
                    if metadata and metadata.name:
                        self._skills_metadata[metadata.name] = metadata
                        successful_paths += 1
                        logger.debug(
                            f"[SkillAgent] Agent '{self.name}': "
                            f"Loaded skill '{metadata.name}' from '{skill_path}'"
                        )
                    else:
                        failed_paths += 1
                        logger.warning(
                            f"[SkillAgent] Agent '{self.name}': "
                            f"Failed to load skill from '{skill_path}'"
                        )
                else:
                    # Treat as parent directory, search for skills recursively
                    skill_files = list(skill_path.rglob("SKILL.md"))
                    path_skill_count = 0

                    for skill_file in skill_files:
                        # Skip files in non-skill subdirectories
                        try:
                            rel_parts = skill_file.relative_to(skill_path).parts
                            if any(p in non_skill_subdirs for p in rel_parts[1:-1]):
                                continue
                        except Exception:
                            pass

                        metadata = _load_metadata_from_file(skill_file)
                        if metadata and metadata.name:
                            self._skills_metadata[metadata.name] = metadata
                            path_skill_count += 1

                    if path_skill_count > 0:
                        successful_paths += 1
                        logger.debug(
                            f"[SkillAgent] Agent '{self.name}': "
                            f"Loaded {path_skill_count} skills from '{skill_path}'"
                        )
                    else:
                        failed_paths += 1
                        logger.warning(
                            f"[SkillAgent] Agent '{self.name}': "
                            f"No skills discovered from '{skill_path}'"
                        )

            except Exception as e:
                failed_paths += 1
                logger.error(
                    f"[SkillAgent] Agent '{self.name}': "
                    f"Failed to load skills from '{skill_path_str}': {e}",
                    exc_info=True
                )

        # Summary log
        logger.info(
            f"[SkillAgent] Agent '{self.name}': "
            f"Discovery complete - {self.skills_count} unique skills "
            f"from {successful_paths}/{len(self.skills)} path(s) "
            f"({failed_paths} failed)"
        )

    async def _build_skill_prompt(self) -> None:
        """Build skill prompt section from discovered skill metadata.

        Creates a formatted markdown skill list and injects it into the
        agent's additional_prompt, providing the LLM with awareness of
        available skills.

        Process:
            1. Return early if no skills discovered
            2. Build sorted skill entries with name, description, args, and path
            3. Format using skill_prompt_template
            4. Append to additional_prompt (or replace if empty)

        Log:
            - DEBUG: Prompt size and skill count
        """
        if not self._skills_metadata:
            logger.debug(
                f"[SkillAgent] Agent '{self.name}': "
                f"No skills to add to prompt"
            )
            return

        # Build skill list (sorted for consistency)
        skill_entries = []
        for name, meta in sorted(self._skills_metadata.items()):
            # Build entry with name and description
            entry = f"## {name}\n{meta.description}"

            # Add SKILL.md path for reference
            if hasattr(meta, 'skill_path') and meta.skill_path:
                entry += f'\nCheck "{meta.skill_path}" for how to use this skill'

            skill_entries.append(entry)

        skill_list = "\n\n".join(skill_entries)

        # Generate skill prompt
        skill_prompt = self.skill_prompt_template.format(skill_list=skill_list)

        # Enhance additional_prompt
        if self.additional_prompt:
            self.additional_prompt = f"{self.additional_prompt}\n\n{skill_prompt}"
        else:
            self.additional_prompt = skill_prompt

        logger.debug(
            f"[SkillAgent] Agent '{self.name}': "
            f"Injected skill prompt ({len(skill_prompt)} chars) "
            f"for {len(skill_entries)} skills"
        )

    def get_skill_metadata(self, skill_name: str) -> Optional[SkillMetadata]:
        """Get metadata for a specific skill.

        Args:
            skill_name: Name of the skill to retrieve.

        Returns:
            SkillMetadata if found, None otherwise.

        Example:
            >>> meta = agent.get_skill_metadata("code-review")
            >>> if meta:
            ...     print(f"Description: {meta.description}")
        """
        return self._skills_metadata.get(skill_name)

    def list_skills(self) -> List[str]:
        """List all available skill names.

        Returns:
            Sorted list of skill names.

        Note:
            This is an alias for the skill_names property.
        """
        return self.skill_names