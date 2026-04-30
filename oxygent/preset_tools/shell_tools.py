"""Shell command execution tools for OxyGent agents."""

import asyncio
import logging
import subprocess
from typing import List, Optional

from pydantic import Field

from oxygent.oxy import FunctionHub

logger = logging.getLogger(__name__)
shell_tools = FunctionHub(name="shell_tools")


@shell_tools.tool(description="Run a shell command and return the output or error.")
def run_shell_command(
    args: List[str] = Field(description="command arguments"),
    tail: int = 10,
    base_dir: Optional[str] = None,
) -> str:
    """Runs a shell command and returns the output or error."""

    try:
        logger.info(f"Running shell command: {args}")
        result = subprocess.run(
            args,
            capture_output=True,
            encoding="utf8",
            shell=True,
            text=True,
            cwd=base_dir,
        )
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return "\n".join(result.stdout.split("\n")[-tail:])
    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        return f"Error: {e}"


@shell_tools.tool(
    description="Execute a shell command asynchronously and return the return code, "
    "standard output and standard error. Supports timeout for long-running commands."
)
async def execute_shell_command(
    command: str,
    timeout: int = 300,
) -> str:
    """Execute given shell command and return the result.

    Args:
        command: The shell command to execute.
        timeout: Maximum time (in seconds) allowed for the command to run. Defaults to 300.

    Returns:
        A formatted string containing returncode, stdout, and stderr.
    """
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        bufsize=0,
    )

    try:
        await asyncio.wait_for(proc.wait(), timeout=timeout)
        stdout, stderr = await proc.communicate()
        stdout_str = stdout.decode("utf-8")
        stderr_str = stderr.decode("utf-8")
        returncode = proc.returncode

    except asyncio.TimeoutError:
        stderr_suffix = (
            f"TimeoutError: The command execution exceeded "
            f"the timeout of {timeout} seconds."
        )
        returncode = -1
        try:
            proc.terminate()
            stdout, stderr = await proc.communicate()
            stdout_str = stdout.decode("utf-8")
            stderr_str = stderr.decode("utf-8")
            if stderr_str:
                stderr_str += f"\n{stderr_suffix}"
            else:
                stderr_str = stderr_suffix
        except ProcessLookupError:
            stdout_str = ""
            stderr_str = stderr_suffix

    return (
        f"<returncode>{returncode}</returncode>"
        f"<stdout>{stdout_str}</stdout>"
        f"<stderr>{stderr_str}</stderr>"
    )
