from __future__ import annotations

from pathlib import Path

from .agent_runner import run_command
from .models import CommandResult


class GeminiRunner:
    provider = "gemini"
    reasoning_effort = None

    def __init__(self, command: str, model: str | None, sandbox: str):
        self.command = command
        self.model = model
        self.sandbox = sandbox

    def build_command(self, *, instruction: str, workspace: Path, output_last_message: Path) -> tuple[str, ...]:
        args: list[str] = [self.command]
        if self.model and self.model.casefold() != "auto":
            args += ["--model", self.model]
        args += ["--prompt", instruction, "--output-format", "stream-json", "--approval-mode", "yolo"]
        return tuple(args)

    def run(self, *, instruction: str, workspace: Path, output_last_message: Path, stdout_log: Path, stderr_log: Path, timeout_seconds: int) -> CommandResult:
        command = self.build_command(instruction=instruction, workspace=workspace, output_last_message=output_last_message)
        result = run_command(command, workspace=workspace, stdout_log=stdout_log, stderr_log=stderr_log, timeout_seconds=timeout_seconds)
        # Gemini has no --output-last-message equivalent; preserve stdout for diagnostics.
        output_last_message.parent.mkdir(parents=True, exist_ok=True)
        output_last_message.write_text(result.stdout, encoding="utf-8")
        return result
