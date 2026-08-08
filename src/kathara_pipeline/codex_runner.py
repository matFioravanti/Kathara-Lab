from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from .exceptions import CodexAuthenticationError, CodexExecutionError, CodexSignalError
from .models import CommandResult


_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s\"']+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"(?i)((?:openai[_-]?api[_-]?key|api[_-]?key|access[_-]?token|cookie)\s*[=:]\s*)[^\s\"']+"),
)


def _redact_sensitive(text: str) -> str:
    redacted = text
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(r"\1[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _resolved_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def redact_command(command: list[str] | tuple[str, ...]) -> list[str]:
    """Return argv safe to persist in manifests and error metadata."""

    redacted = [_redact_sensitive(argument) for argument in command]
    if len(redacted) > 2 and redacted[1] == "exec":
        redacted[-1] = "<instruction>"
    return redacted


def process_metadata_from_result(
    result: CommandResult,
    *,
    cwd: Path,
    jsonl_log: Path,
    stderr_log: Path,
) -> dict[str, Any]:
    """Build manifest-safe Codex metadata from a completed process result."""

    return {
        "command": redact_command(result.command),
        "return_code": result.return_code,
        "duration_seconds": result.duration_seconds,
        "timed_out": result.timed_out,
        "cwd": str(cwd),
        "working_directory": str(cwd),
        "jsonl_log": str(jsonl_log),
        "stderr_log": str(stderr_log),
        "malformed_json_lines": list(result.malformed_json_lines),
    }


class CodexRunner:
    """Execute one non-interactive Codex turn and retain its raw logs.

    ``run`` deliberately owns exactly one ``subprocess.run`` call.  Callers own
    the isolated workspace and decide which generated artifact to collect.
    """

    def __init__(
        self,
        *,
        command: str = "codex",
        sandbox: str = "workspace-write",
        timeout_seconds: float = 1800,
        approval_policy: str = "never",
    ) -> None:
        if sandbox not in {"read-only", "workspace-write", "danger-full-access"}:
            raise ValueError(f"Unsupported Codex sandbox: {sandbox}")
        if sandbox == "danger-full-access":
            raise ValueError("danger-full-access is not permitted by this pipeline")
        if timeout_seconds <= 0:
            raise ValueError("Codex timeout must be positive")
        if approval_policy not in {"untrusted", "on-request", "never"}:
            raise ValueError(f"Unsupported approval policy: {approval_policy}")
        self.command = command
        self.sandbox = sandbox
        self.timeout_seconds = timeout_seconds
        self.approval_policy = approval_policy

    def build_command(
        self,
        *,
        workspace: Path,
        output_last_message: Path,
        instruction: str,
    ) -> list[str]:
        """Build the argv accepted by Codex CLI 0.146.0.

        ``--ask-for-approval`` is a global-only option in that release.  The
        equivalent exec-local configuration override keeps ``exec`` in the
        stable second argv position and avoids any interactive approval wait.
        """

        if not instruction.strip():
            raise ValueError("Codex instruction cannot be empty")
        return [
            self.command,
            "exec",
            "--model",
            "gpt-5.6-terra",
            "-c",
            'model_reasoning_effort="low"',
            "-c",
            f'approval_policy="{self.approval_policy}"',
            "--sandbox",
            self.sandbox,
            "--cd",
            str(workspace),
            "--json",
            "--output-last-message",
            str(output_last_message),
            "--ephemeral",
            instruction,
        ]

    def run(
        self,
        *,
        instruction: str,
        workspace: Path,
        output_last_message: Path,
        jsonl_log: Path,
        stderr_log: Path,
        timeout_seconds: float | None = None,
    ) -> CommandResult:
        """Run Codex once, validate JSONL completion, and return process data."""

        workspace = workspace.resolve()
        if not workspace.is_dir():
            raise CodexExecutionError(f"Codex workspace does not exist: {workspace}")
        if not _resolved_inside(output_last_message, workspace):
            raise CodexExecutionError(
                "Codex final-message path must remain inside its isolated workspace"
            )

        effective_timeout = self.timeout_seconds if timeout_seconds is None else timeout_seconds
        if effective_timeout <= 0:
            raise ValueError("Codex timeout must be positive")

        output_last_message.parent.mkdir(parents=True, exist_ok=True)
        jsonl_log.parent.mkdir(parents=True, exist_ok=True)
        stderr_log.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command(
            workspace=workspace,
            output_last_message=output_last_message,
            instruction=instruction,
        )
        metadata_base = {
            "command": redact_command(command),
            "cwd": str(workspace),
            "working_directory": str(workspace),
            "jsonl_log": str(jsonl_log),
            "stderr_log": str(stderr_log),
        }
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                shell=False,
                cwd=workspace,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=effective_timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            duration = time.monotonic() - started
            self._write_logs(jsonl_log, stderr_log, "", str(exc))
            raise CodexExecutionError(
                f"Codex command not found: {self.command}",
                details=(f"duration_seconds={duration:.6f}",),
                process_metadata={
                    **metadata_base,
                    "return_code": None,
                    "duration_seconds": duration,
                    "timed_out": False,
                    "malformed_json_lines": [],
                },
            ) from exc
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - started
            stdout = _as_text(exc.stdout)
            stderr = _as_text(exc.stderr)
            self._write_logs(jsonl_log, stderr_log, stdout, stderr)
            raise CodexExecutionError(
                f"Codex timed out after {effective_timeout:g} seconds",
                details=(f"duration_seconds={duration:.6f}",),
                process_metadata={
                    **metadata_base,
                    "return_code": None,
                    "duration_seconds": duration,
                    "timed_out": True,
                    "malformed_json_lines": self._inspect_jsonl(stdout)[0],
                },
            ) from exc
        except OSError as exc:
            duration = time.monotonic() - started
            self._write_logs(jsonl_log, stderr_log, "", str(exc))
            raise CodexExecutionError(
                f"Codex process could not be started: {exc}",
                details=(f"duration_seconds={duration:.6f}",),
                process_metadata={
                    **metadata_base,
                    "return_code": None,
                    "duration_seconds": duration,
                    "timed_out": False,
                    "malformed_json_lines": [],
                },
            ) from exc

        duration = time.monotonic() - started
        stdout = _as_text(completed.stdout)
        stderr = _as_text(completed.stderr)
        self._write_logs(jsonl_log, stderr_log, stdout, stderr)
        malformed, completed_turn = self._inspect_jsonl(stdout)
        result = CommandResult(
            command=tuple(command),
            return_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            malformed_json_lines=tuple(malformed),
        )
        process_metadata = {
            **metadata_base,
            "return_code": completed.returncode,
            "duration_seconds": duration,
            "timed_out": False,
            "malformed_json_lines": malformed,
        }

        if completed.returncode != 0:
            if completed.returncode < 0:
                raise CodexSignalError(
                    f"Codex was terminated by signal {-completed.returncode}",
                    details=(_redact_sensitive(stderr.strip()) or "no stderr",),
                    process_metadata=process_metadata,
                )
            diagnostics = f"{stdout}\n{stderr}"
            if re.search(r"(?i)\b(?:auth(?:entication)?|login|unauthorized|401)\b", diagnostics):
                raise CodexAuthenticationError(
                    "Codex authentication is unavailable or expired",
                    details=(_redact_sensitive(stderr.strip()) or "no stderr",),
                    process_metadata=process_metadata,
                )
            raise CodexExecutionError(
                f"Codex exited with return code {completed.returncode}",
                details=(_redact_sensitive(stderr.strip()) or "no stderr",),
                process_metadata=process_metadata,
            )
        if not completed_turn:
            detail = (
                f"malformed JSONL lines: {', '.join(map(str, malformed))}"
                if malformed
                else "stdout contained no turn.completed event"
            )
            raise CodexExecutionError(
                "Codex JSONL stream did not contain a valid turn.completed event",
                details=(detail,),
                process_metadata=process_metadata,
            )
        if not output_last_message.is_file():
            raise CodexExecutionError(
                f"Codex did not write its final message: {output_last_message}",
                process_metadata=process_metadata,
            )
        if output_last_message.is_symlink() or not _resolved_inside(output_last_message, workspace):
            raise CodexExecutionError(
                "Codex final-message output escaped the workspace",
                process_metadata=process_metadata,
            )
        try:
            if not output_last_message.read_text(encoding="utf-8").strip():
                raise CodexExecutionError(
                    "Codex final-message output is empty",
                    process_metadata=process_metadata,
                )
        except (OSError, UnicodeError) as exc:
            raise CodexExecutionError(
                "Codex final-message output is unreadable",
                process_metadata=process_metadata,
            ) from exc
        return result

    @staticmethod
    def _write_logs(
        jsonl_log: Path,
        stderr_log: Path,
        stdout: str,
        stderr: str,
    ) -> None:
        jsonl_log.write_text(_redact_sensitive(stdout), encoding="utf-8")
        stderr_log.write_text(_redact_sensitive(stderr), encoding="utf-8")

    @staticmethod
    def _inspect_jsonl(stdout: str) -> tuple[list[int], bool]:
        malformed: list[int] = []
        completed_turn = False
        for line_number, raw_line in enumerate(stdout.splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                event: Any = json.loads(raw_line)
            except (json.JSONDecodeError, UnicodeError):
                malformed.append(line_number)
                continue
            if not isinstance(event, dict):
                malformed.append(line_number)
                continue
            if event.get("type") == "turn.completed":
                completed_turn = True
        return malformed, completed_turn
