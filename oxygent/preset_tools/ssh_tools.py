"""SSH remote execution tools for OxyGent agents."""

import asyncio
from typing import Optional

from pydantic import Field

from .. import OxyRequest
from ..utils.common_utils import clean_ansi_codes
from . import FunctionHub

ssh_tools = FunctionHub(name="ssh_tools", timeout=600)


@ssh_tools.tool(description="a tool for control the ubuntu terminal")
async def ssh_tool(
    shell_command: str = Field(description="The shell command to execute"),
    oxy_request: Optional[OxyRequest] = None,
) -> str:
    ssh_channel = oxy_request.get_global_data("ssh_channel")
    ssh_channel.send(f"{shell_command}\n")

    lines_merged = ""
    skip_count = 0
    while True:
        await asyncio.sleep(0.1)

        if ssh_channel.recv_ready():
            output = ssh_channel.recv(1024).decode("utf-8", errors="ignore")
            output = clean_ansi_codes(output)
            if output:
                lines_merged += output
                if "vboxuser@ubuntu" in lines_merged:
                    break
                if "password for vboxuser" in lines_merged:
                    break
                if "y/n" in output.lower():
                    break
                if "[y]" in output and "[n]" in output:
                    break
            else:
                skip_count += 1
        else:
            skip_count += 1

    if len(lines_merged) > 1000:
        return (
            lines_merged[:500]
            + "<<<Due to excessive length, this part is omitted when displayed.>>>"
            + lines_merged[-500:]
        )
    return lines_merged
