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

from ...prompts import SYSTEM_PROMPT_SKILLS
from ...schemas import OxyRequest
from ...schemas.skill import SkillMetadata
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
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
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

    prompt: Optional[str] = Field(
        default=SYSTEM_PROMPT_SKILLS,
        description="Defaults to 'SYSTEM_PROMPT', the prompt to initialize the agent's behavior.",
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
        self._skill_entries = []
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
            logger.debug(f"[SkillAgent] Agent '{self.name}': No skill paths configured")
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
                    skill_files = list(skill_path.glob("*/SKILL.md"))
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
                    exc_info=True,
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

        Log:
            - DEBUG: Prompt size and skill count
        """
        if not self._skills_metadata:
            logger.debug(
                f"[SkillAgent] Agent '{self.name}': No skills to add to prompt"
            )
            return

        # Build skill list (sorted for consistency)
        self._skill_entries = []
        for name, meta in sorted(self._skills_metadata.items()):
            # Build entry with name and description
            entry = f"## {name}\n{meta.description}"

            # Add SKILL.md path for reference
            if hasattr(meta, "skill_path") and meta.skill_path:
                entry += f'\nCheck "{meta.skill_path}" for how to use this skill'

            self._skill_entries.append(entry)

    async def _before_execute(self, oxy_request: OxyRequest) -> OxyRequest:
        """Prepare skill context before execution."""
        oxy_request = await super()._before_execute(oxy_request)
        if not oxy_request.has_arguments("skill_list"):
            oxy_request.set_arguments("skill_list", "\n\n".join(self._skill_entries))
        return oxy_request
