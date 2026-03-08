import asyncio
import logging
import shlex
import subprocess
from typing import List, Optional

from pydantic import Field

from oxygent.oxy import FunctionHub

logger = logging.getLogger(__name__)
shell_tools = FunctionHub(name="shell_tools")


@shell_tools.tool(
    description="Run a shell command and return the output or error. "
                "Supports timeout control, tail output (last N lines), working directory, and structured return format. "
                "For long-running commands, consider using execute_shell_command_async instead."
)
def run_shell_command(
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        tail: int = Field(
            default=10,
            description="Return only the last N lines of output. Use -1 for all lines."
        ),
        base_dir: Optional[str] = Field(
            default=None,
            description="Working directory for the command. If not specified, uses current directory."
        ),
        timeout: int = Field(
            default=60,
            description="Timeout in seconds for command execution. Default is 60 seconds."
        ),
        return_structured: bool = Field(
            default=False,
            description="If True, return structured format with returncode, stdout, stderr. "
                        "If False (default), return only stdout."
        )
) -> str:
    """Runs a shell command and returns the output or error.

    This is a synchronous version suitable for simple commands.
    For long-running or complex commands, use execute_shell_command_async.

    Args:
        command: The shell command to execute. If None, will be constructed from args.
        args: Alternative way to provide command as a list of arguments.
        tail: Return only the last N lines of output. Use -1 for all lines.
        base_dir: Working directory for the command.
        timeout: Timeout in seconds. Default is 60 seconds.
        return_structured: If True, return structured format with returncode, stdout, stderr.

    Returns:
        Command output or error message. If return_structured=True, returns XML-like format.
    """
    try:
        if command is None:
            args = args or []
            command = " ".join(shlex.quote(str(a)) for a in args)

        logger.info("Running shell command: %s (timeout: %ds)", command, timeout)

        result = subprocess.run(
            command,
            capture_output=True,
            encoding="utf8",
            shell=True,
            text=True,
            cwd=base_dir,
            timeout=timeout
        )

        stdout_lines = result.stdout.split("\n")
        if tail > 0 and len(stdout_lines) > tail:
            stdout_output = "\n".join(stdout_lines[-tail:])
        else:
            stdout_output = result.stdout

        stderr_output = result.stderr

        if return_structured:
            return (
                f"<returncode>{result.returncode}</returncode>\n"
                f"<stdout>{stdout_output}</stdout>\n"
                f"<stderr>{stderr_output}</stderr>"
            )

        if result.returncode != 0:
            if stderr_output:
                return f"Error: {stderr_output}"
            return f"Command returned non-zero exit code: {result.returncode}"

        return stdout_output

    except subprocess.TimeoutExpired:
        error_msg = f"TimeoutError: The command execution exceeded the timeout of {timeout} seconds."
        logger.warning(error_msg)
        if return_structured:
            return (
                f"<returncode>-1</returncode>\n"
                f"<stdout></stdout>\n"
                f"<stderr>{error_msg}</stderr>"
            )
        return f"Error: {error_msg}"

    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        if return_structured:
            return (
                f"<returncode>-1</returncode>\n"
                f"<stdout></stdout>\n"
                f"<stderr>Error: {e}</stderr>"
            )
        return f"Error: {e}"


@shell_tools.tool(
    description="Execute a shell command asynchronously and return structured output with returncode, stdout, and stderr. "
                "Supports timeout control and automatically terminates the process on timeout. "
                "Recommended for long-running commands."
)
async def execute_shell_command_async(
        command: str = Field(description="The shell command to execute."),
        timeout: int = Field(
            default=300,
            description="Maximum time (in seconds) allowed for the command to run. Defaults to 300 seconds (5 minutes)."
        ),
) -> str:
    """Execute given shell command asynchronously and return the result.

    This is an asynchronous version suitable for long-running commands.
    It provides better timeout handling and structured output.

    Args:
        command: The shell command to execute.
        timeout: Maximum time (in seconds) allowed for the command to run. Defaults to 300.

    Returns:
        A formatted string containing returncode, stdout, and stderr in XML-like format.
    """
    logger.info("Running async shell command: %s (timeout: %ds)", command, timeout)

    try:
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
            f"<returncode>{returncode}</returncode>\n"
            f"<stdout>{stdout_str}</stdout>\n"
            f"<stderr>{stderr_str}</stderr>"
        )

    except Exception as e:
        logger.warning(f"Failed to execute async shell command: {e}")
        return (
            f"<returncode>-1</returncode>\n"
            f"<stdout></stdout>\n"
            f"<stderr>Error: {e}</stderr>"
        )


@shell_tools.tool(
    description="Run a shell command and return only the output (stdout). "
                "Simplified version of run_shell_command for quick commands. "
                "Automatically raises an error if the command fails."
)
def run_command_simple(
        command: str = Field(description="The shell command to execute."),
        base_dir: Optional[str] = Field(
            default=None,
            description="Working directory for the command."
        ),
) -> str:
    """Simple wrapper to run a shell command and return output.

    This is a simplified version for quick commands where you only need stdout.
    It will raise an error if the command fails.

    Args:
        command: The shell command to execute.
        base_dir: Working directory for the command.

    Returns:
        Command stdout only.
    """
    try:
        logger.info("Running simple command: %s", command)
        result = subprocess.run(
            command,
            capture_output=True,
            encoding="utf8",
            shell=True,
            text=True,
            cwd=base_dir,
            timeout=30  # Short timeout for simple commands
        )

        if result.returncode != 0:
            raise Exception(f"Command failed with exit code {result.returncode}: {result.stderr}")

        return result.stdout

    except subprocess.TimeoutExpired:
        raise Exception("Command timed out after 30 seconds")
    except Exception as e:
        logger.warning(f"Failed to run simple command: {e}")
        raise
