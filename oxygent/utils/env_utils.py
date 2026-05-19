# -*- coding: utf-8 -*-
"""Get environment variables."""

import os
import socket
from typing import Any


def get_env(key: str, default_val: Any = None) -> Any:
    """Get environment variables, return default value if not exist :param key:

    :param default_val:
    :return:
    """
    return os.getenv(key) if os.getenv(key) else default_val


def get_env_for_log_path() -> str:
    """Get log path :return:"""
    return get_env(key="LOG_PATH", default_val="/export/Logs")


def get_env_for_cpu_count() -> int:
    """Get value of available cpu cores :return:"""
    return int(get_env(key="AVAILABLE_CORES", default_val=2))


def get_env_for_run_attr() -> int:
    """Get http service run attr Use in bin/start.sh, only for backups here :return:"""
    try:
        return int(get_env(key="RUN_ATTR", default_val=-1))
    except Exception:
        return -1


def get_schedule_profile() -> str:
    """Get schedule profile, used in task scheduling :return:"""
    return get_env(key="SCHEDULE_JOB", default_val="false")


def get_engine_intelligent_profile() -> str:
    """Get engine intelligent profile, used in task scheduling :return:"""
    return get_env(key="ENGINE", default_val="yachain_group")


def get_env_for_deployment_stage() -> int:
    """Differentiate the running environment :return: int 1-production 2-development
    3-local debug."""
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
    """Get local ip :return: str."""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"
    return local_ip


def get_env_for_group_id() -> int:
    """Get group id of the machine :return: int."""
    group_id = get_env(key="GROUP_ID", default_val="0")
    return int(group_id)
