"""
Live Prompt Management Module
Provides real-time prompt management and hot-reload functionality for OxyGent agents
"""

# Core ES-based prompt management
from .manager import (
    PromptManager,
    close_prompt_manager,
    get_dynamic_prompt,
    get_prompt_manager,
)

# Prompt optimization
from .optimizer import PromptOptimizer, get_prompt_optimizer

# Version synchronization for multi-instance cache consistency
from .version import (
    VersionSyncCoordinator,
    get_version_sync_coordinator,
    start_version_sync,
    stop_version_sync,
)

# Hot-reload functionality
from .wrapper import (
    dynamic_agent_manager,
    hot_reload_agent,
    hot_reload_all_prompts,
    hot_reload_prompt,
    setup_dynamic_agents,
)

__all__ = [
    # Core ES-based prompt management
    "get_prompt_manager",
    "get_dynamic_prompt",
    "close_prompt_manager",
    "PromptManager",
    # Hot-reload functionality
    "setup_dynamic_agents",
    "hot_reload_prompt",
    "hot_reload_agent",
    "hot_reload_all_prompts",
    "dynamic_agent_manager",
    # Version synchronization
    "VersionSyncCoordinator",
    "get_version_sync_coordinator",
    "start_version_sync",
    "stop_version_sync",
    # Prompt optimization
    "get_prompt_optimizer",
    "PromptOptimizer",
]
