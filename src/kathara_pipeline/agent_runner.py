from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Protocol

from .models import CommandResult


class AgentRunner(Protocol):
    provider: str
    model: str | None
    reasoning_effort: str | None

    def build_command(self, *, instruction: str, workspace: Path, output_last_message: Path) -> tuple[str, ...]: ...

    def run(
        self,
        *,
        instruction: str,
        workspace: Path,
        output_last_message: Path,
        stdout_log: Path,
        stderr_log: Path,
        timeout_seconds: int,
    ) -> CommandResult: ...


def run_command(
    command: tuple[str, ...],
    *,
    workspace: Path,
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
) -> CommandResult:
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    stderr_log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        timed_out = False
        return_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        return_code = 124
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        stderr += f"\nProcess timed out after {timeout_seconds}s.\n"
    duration = time.monotonic() - started
    stdout_log.write_text(stdout, encoding="utf-8")
    stderr_log.write_text(stderr, encoding="utf-8")
    return CommandResult(command, return_code, stdout, stderr, duration, timed_out)
