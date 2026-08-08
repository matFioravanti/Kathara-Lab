from __future__ import annotations

from pathlib import Path

from .agent_runner import run_command
from .models import CommandResult


class CodexRunner:
    provider = "codex"

    def __init__(self, command: str, model: str | None, reasoning_effort: str | None, sandbox: str):
        self.command = command
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.sandbox = sandbox

    def build_command(self, *, instruction: str, workspace: Path, output_last_message: Path) -> tuple[str, ...]:
        args: list[str] = [self.command, "exec"]
        if self.model:
            args += ["--model", self.model]
        if self.reasoning_effort:
            args += ["-c", f'model_reasoning_effort="{self.reasoning_effort}"']
        args += [
            "-c", 'approval_policy="never"',
            "--sandbox", self.sandbox,
            "--cd", str(workspace),
            "--json",
            "--output-last-message", str(output_last_message),
            "--ephemeral",
            instruction,
        ]
        return tuple(args)

    def run(self, *, instruction: str, workspace: Path, output_last_message: Path, stdout_log: Path, stderr_log: Path, timeout_seconds: int) -> CommandResult:
        command = self.build_command(instruction=instruction, workspace=workspace, output_last_message=output_last_message)
        return run_command(command, workspace=workspace, stdout_log=stdout_log, stderr_log=stderr_log, timeout_seconds=timeout_seconds)
