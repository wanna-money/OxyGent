import asyncio
import logging

from pydantic import Field

from ...schemas import (
    LLMResponse,
    LLMState,
    Memory,
    Message,
    OxyRequest,
    OxyResponse,
    OxyState,
)
from ...utils.common_utils import clean_ansi_codes
from .react_agent import ReActAgent

logger = logging.getLogger(__name__)


class ShellUseAgent(ReActAgent):
    """ReAct-style agent that uses shell/SSH tools to accomplish tasks."""

    auth_info: dict = Field(default_factory=dict)

    async def init(self):
        """Async initialization for the shell-use agent."""
        await super().init()

        import paramiko

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(**self.auth_info)
        ssh_channel = client.invoke_shell()

        await asyncio.sleep(1)
        if ssh_channel.recv_ready():
            output = ssh_channel.recv(4096).decode()
            self.mas.global_data["hello_terminal"] = clean_ansi_codes(output)
        self.mas.global_data["ssh_channel"] = ssh_channel

    def _parse_llm_response(
        self, ori_response: str, oxy_request: OxyRequest = None
    ) -> LLMResponse:
        """Parse the LLM response into a structured action, with shell-specific handling."""
        try:
            # Handle think model format
            if "</think>" in ori_response:
                ori_response = ori_response.split("</think>")[-1].strip()
            # Extract shell code segment
            import re

            matches = re.findall(r"```[\n]*shell(.*?)```", ori_response, re.DOTALL)
            json_texts = [match.strip() for match in matches]

            if not json_texts:
                return LLMResponse(
                    state=LLMState.ANSWER
                    if ori_response.startswith("python3 send_email.py")
                    else LLMState.TOOL_CALL,
                    output=ori_response,
                    ori_response=ori_response,
                )
            json_text = json_texts[0] if json_texts else ori_response
            if json_text.startswith("python3 send_email.py"):
                return LLMResponse(
                    state=LLMState.ANSWER,
                    output=json_text,
                    ori_response=ori_response,
                )
            return LLMResponse(
                state=LLMState.TOOL_CALL,
                output=json_text,
                ori_response=ori_response,
            )
        except Exception as e:
            logger.warning(e)
            return LLMResponse(
                state=LLMState.ERROR_PARSE, output=e, ori_response=ori_response
            )

    async def _execute(self, oxy_request: OxyRequest) -> OxyResponse:
        """Run the ReAct loop using shell/SSH tool invocations."""

        def mock_receive_email(query):
            return f"python3 receive_email.py Bob\n{query}\nvboxuser@ubuntu:~$ "

        oxy_request.set_query(mock_receive_email(oxy_request.get_query()))
        oxy_request.set_arguments(
            "hello_terminal", oxy_request.get_global_data("hello_terminal")
        )

        react_memory = Memory()
        for current_round in range(self.max_react_rounds + 1):
            # Build complete message context: instruction + short memory + query + react memory
            terminal_history = ""
            terminal_history += "".join(
                [
                    message["content"]
                    for message in oxy_request.get_short_memory()
                    if not message["content"].startswith("cmd: ")
                ]
            )
            terminal_history += oxy_request.get_query()
            terminal_history += "".join(
                [
                    message.content
                    for message in react_memory.messages
                    if message.role == "user"
                ]
            )
            oxy_request.set_arguments("terminal_history", terminal_history)

            temp_memory = Memory()
            temp_memory.add_message(
                Message.system_message(self._build_instruction(oxy_request.arguments))
            )
            temp_memory.add_message(
                Message.user_message(
                    "Please continue working on the Ubuntu terminal to complete the boss’s task."
                )
            )

            full_memory = temp_memory.to_dict_list()
            oxy_response = await oxy_request.call(
                callee=self.llm_model,
                arguments={"messages": full_memory},
            )
            oxy_request.arguments["full_memory"] = full_memory
            llm_response = self.func_parse_llm_response(
                oxy_response.output, oxy_request
            )

            # Execute based on LLM decision
            if llm_response.state is LLMState.ANSWER:
                return OxyResponse(
                    state=OxyState.COMPLETED,
                    output=llm_response.output + "\nvboxuser@ubuntu:~$ ",
                    extra={"react_memory": react_memory.to_dict_list()},
                )
            elif llm_response.state is LLMState.TOOL_CALL:
                oxy_response = await oxy_request.call(
                    callee="ssh_tool",
                    arguments={"shell_command": llm_response.output},
                )
                react_memory.add_message(
                    Message.assistant_message("cmd: " + llm_response.output)
                )
                react_memory.add_message(Message.user_message(oxy_response.output))
            else:
                # Parsing error - add to memory for correction
                logger.info(
                    f"Format error, adding to react_memory: {llm_response.ori_response}",
                    extra={
                        "trace_id": oxy_request.current_trace_id,
                        "node_id": oxy_request.node_id,
                    },
                )
                react_memory.add_message(
                    Message.assistant_message(llm_response.ori_response)
                )
                react_memory.add_message(Message.user_message(llm_response.output))

        # Fallback mechanism when max rounds reached
        # Extract tool call results for final summary
        tid = 1
        tool_call_results = []
        for message in react_memory.to_dict_list():
            if message["role"] != "user":
                continue
            tool_call_results.append(str(tid) + ". " + message["content"])
            tid += 1
        tool_call_results = "\n\n".join(tool_call_results)

        # Generate final answer based on accumulated results
        query = oxy_request.get_query()
        temp_messages = [
            Message.system_message(
                "Please answer the user's question based on the given tool execution results."
            ),
            Message.user_message(
                f"User question: {query}\n---\nTool execution results: {tool_call_results}"
            ),
        ]
        oxy_response = await oxy_request.call(
            callee=self.llm_model,
            arguments={"messages": [msg.to_dict() for msg in temp_messages]},
        )

        return OxyResponse(
            state=OxyState.COMPLETED,
            output=oxy_response.output,
            extra={"react_memory": react_memory.to_dict_list()},
        )
