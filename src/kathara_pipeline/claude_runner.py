from __future__ import annotations

from pathlib import Path

from .agent_runner import run_command
from .models import CommandResult


class ClaudeRunner:
    provider = "claude"

    def __init__(self, command: str, model: str | None, reasoning_effort: str | None):
        self.command = command
        self.model = model
        self.reasoning_effort = reasoning_effort

    def build_command(self, *, instruction: str, workspace: Path, output_last_message: Path) -> tuple[str, ...]:
        # --safe-mode keeps normal authentication while disabling local CLAUDE.md/skills/plugins/MCP.
        # Restrict built-in tools to the minimum needed for an isolated file-generation workspace.
        args: list[str] = [
            self.command,
            "--safe-mode",
            "--print",
            instruction,
            "--output-format", "stream-json",
            "--permission-mode", "bypassPermissions",
            "--tools", "Read,Write,Edit",
            "--no-session-persistence",
            "--no-chrome",
        ]
        if self.model:
            args += ["--model", self.model]
        if self.reasoning_effort:
            args += ["--effort", self.reasoning_effort]
        return tuple(args)

    def run(self, *, instruction: str, workspace: Path, output_last_message: Path, stdout_log: Path, stderr_log: Path, timeout_seconds: int) -> CommandResult:
        command = self.build_command(instruction=instruction, workspace=workspace, output_last_message=output_last_message)
        result = run_command(command, workspace=workspace, stdout_log=stdout_log, stderr_log=stderr_log, timeout_seconds=timeout_seconds)
        output_last_message.parent.mkdir(parents=True, exist_ok=True)
        output_last_message.write_text(result.stdout, encoding="utf-8")
        return result
