"""Environment variable access utilities.

Provides typed getters for environment variables with sensible defaults,
including deployment stage detection, resource limits, and network identity.
"""

import logging
import os
import socket
from typing import Any

logger = logging.getLogger(__name__)


def get_env(key: str, default_val: Any = None) -> Any:
    """Get an environment variable, falling back to a default.

    Args:
        key: Environment variable name.
        default_val: Value returned when the variable is unset.

    Returns:
        The environment variable value, or *default_val*.
    """
    return os.getenv(key) if os.getenv(key) else default_val


def get_env_for_log_path() -> str:
    """Get the configured log directory path."""
    return get_env(key="LOG_PATH", default_val="/export/Logs")


def get_env_for_cpu_count() -> int:
    """Get the number of available CPU cores (default 2)."""
    return int(get_env(key="AVAILABLE_CORES", default_val=2))


def get_env_for_run_attr() -> int:
    """Get HTTP service run attribute (used in bin/start.sh)."""
    try:
        return int(get_env(key="RUN_ATTR", default_val=-1))
    except Exception as e:
        logger.debug(f"Failed to parse RUN_ATTR as int: {e}", exc_info=True)
        return -1


def get_schedule_profile() -> str:
    """Get the schedule job profile flag."""
    return get_env(key="SCHEDULE_JOB", default_val="false")


def get_engine_intelligent_profile() -> str:
    """Get the engine intelligent profile name."""
    return get_env(key="ENGINE", default_val="yachain_group")


def get_env_for_deployment_stage() -> int:
    """Get the deployment stage as an integer code.

    Returns:
        1 for production, 2 for development, 3 for local debug.
    """
    deployment_stage = get_env(key="DEPLOYMENT_STAGE", default_val="local")
    if deployment_stage == "prod":
        return 1
    elif deployment_stage == "dev":
        return 2
    else:
        return 3


def is_prod_env() -> bool:
    """Return True when the application is running in a production environment."""
    deployment_stage = get_env(key="DEPLOYMENT_STAGE", default_val="local")
    return deployment_stage == "prod"


def get_local_ip() -> str:
    """Get the local machine's IP address."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        logger.debug(f"Failed to resolve local IP from hostname: {e}", exc_info=True)
        local_ip = "127.0.0.1"
    return local_ip


def get_env_for_group_id() -> int:
    """Get the machine's group ID (default 0)."""
    group_id = get_env(key="GROUP_ID", default_val="0")
    return int(group_id)
