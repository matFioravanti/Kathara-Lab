from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from .codex_runner import _as_text, redact_command
from .exceptions import CheckerExecutionError, LabGenerationError
from .lab_generator import _copy_tree_safely, _is_inside
from .models import CheckerRunResult, JobPaths
from .paths import safe_rmtree
from .state_store import hash_directory, write_json_atomic


class CheckerRunner:
    """Prepare a disposable lab copy and invoke the checker exactly once."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 1800,
        report_type: str = "csv",
        no_cache: bool = True,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("Checker timeout must be positive")
        if report_type != "csv":
            raise ValueError("The pipeline result parser requires CSV checker reports")
        if not no_cache:
            raise ValueError("Checker execution must use --no-cache")
        self.timeout_seconds = timeout_seconds
        self.report_type = report_type
        self.no_cache = no_cache

    def build_command(
        self,
        *,
        correction_path: Path,
        labs_directory: Path,
    ) -> list[str]:
        command = [
            sys.executable,
            "-m",
            "kathara_lab_checker",
            "--config",
            str(correction_path),
            "--labs",
            str(labs_directory),
        ]
        command.append("--no-cache")
        command.extend(("--report-type", self.report_type))
        return command

    def prepare_candidate(self, job_paths: JobPaths) -> dict[str, str]:
        if not job_paths.source.is_dir() or job_paths.source.is_symlink():
            raise CheckerExecutionError("Validated source laboratory is missing")
        if not _is_inside(job_paths.checker_run, job_paths.root):
            raise CheckerExecutionError("Checker run directory escapes the current job")

        generated_root = job_paths.root.parent
        if job_paths.checker_run.exists() or job_paths.checker_run.is_symlink():
            safe_rmtree(job_paths.checker_run, generated_root)
        job_paths.labs_dir.mkdir(parents=True, exist_ok=True)
        try:
            _copy_tree_safely(job_paths.source, job_paths.candidate)
        except LabGenerationError as exc:
            raise CheckerExecutionError(
                "Source laboratory cannot be copied safely for checker execution",
                details=(str(exc),),
            ) from exc

        source_hashes = hash_directory(job_paths.source)
        candidate_hashes = hash_directory(job_paths.candidate)
        if source_hashes != candidate_hashes:
            raise CheckerExecutionError("Checker candidate copy differs from immutable source")
        write_json_atomic(
            job_paths.checker_run / "copied-files.sha256.json",
            {
                "source": str(job_paths.source),
                "candidate": str(job_paths.candidate),
                "files": candidate_hashes,
            },
        )
        return candidate_hashes

    def run(
        self,
        job_paths: JobPaths,
        *,
        correction_path: Path | None = None,
        prepared: bool = False,
    ) -> CheckerRunResult:
        correction = job_paths.correction if correction_path is None else correction_path
        if not correction.is_file() or correction.is_symlink():
            raise CheckerExecutionError(f"Validated correction file is missing: {correction}")
        if not _is_inside(correction, job_paths.root):
            raise CheckerExecutionError("Correction path escapes the current job")

        if prepared:
            if not job_paths.candidate.is_dir() or job_paths.candidate.is_symlink():
                raise CheckerExecutionError("Prepared checker candidate is missing")
            if hash_directory(job_paths.source) != hash_directory(job_paths.candidate):
                raise CheckerExecutionError("Prepared checker candidate differs from immutable source")
        else:
            self.prepare_candidate(job_paths)
        source_before = hash_directory(job_paths.source)
        command = self.build_command(
            correction_path=correction,
            labs_directory=job_paths.labs_dir,
        )
        stdout_log = job_paths.logs / "checker.stdout.log"
        stderr_log = job_paths.logs / "checker.stderr.log"
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        metadata_base = {
            "command": redact_command(command),
            "cwd": str(job_paths.checker_run),
            "working_directory": str(job_paths.checker_run),
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
        }
        started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                shell=False,
                cwd=job_paths.checker_run,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - started
            stdout = _as_text(exc.stdout)
            stderr = _as_text(exc.stderr)
            self._write_logs(stdout_log, stderr_log, stdout, stderr)
            raise CheckerExecutionError(
                f"kathara_lab_checker timed out after {self.timeout_seconds:g} seconds",
                details=(f"duration_seconds={duration:.6f}",),
                process_metadata={
                    **metadata_base,
                    "return_code": None,
                    "duration_seconds": duration,
                    "timed_out": True,
                },
            ) from exc
        except FileNotFoundError as exc:
            duration = time.monotonic() - started
            self._write_logs(stdout_log, stderr_log, "", str(exc))
            raise CheckerExecutionError(
                "Python executable for kathara_lab_checker was not found",
                details=(f"duration_seconds={duration:.6f}",),
                process_metadata={
                    **metadata_base,
                    "return_code": None,
                    "duration_seconds": duration,
                    "timed_out": False,
                },
            ) from exc
        except OSError as exc:
            duration = time.monotonic() - started
            self._write_logs(stdout_log, stderr_log, "", str(exc))
            raise CheckerExecutionError(
                f"kathara_lab_checker could not be started: {exc}",
                details=(f"duration_seconds={duration:.6f}",),
                process_metadata={
                    **metadata_base,
                    "return_code": None,
                    "duration_seconds": duration,
                    "timed_out": False,
                },
            ) from exc

        duration = time.monotonic() - started
        stdout = _as_text(completed.stdout)
        stderr = _as_text(completed.stderr)
        self._write_logs(stdout_log, stderr_log, stdout, stderr)
        process_metadata = {
            **metadata_base,
            "return_code": completed.returncode,
            "duration_seconds": duration,
            "timed_out": False,
        }
        if hash_directory(job_paths.source) != source_before:
            raise CheckerExecutionError(
                "Checker execution modified the immutable source laboratory",
                process_metadata=process_metadata,
            )
        if completed.returncode != 0:
            raise CheckerExecutionError(
                f"kathara_lab_checker exited with return code {completed.returncode}",
                details=(stderr.strip() or "no stderr",),
                process_metadata=process_metadata,
            )
        return CheckerRunResult(
            command=tuple(command),
            return_code=completed.returncode,
            duration_seconds=duration,
            stdout=stdout,
            stderr=stderr,
        )

    @staticmethod
    def _write_logs(
        stdout_log: Path,
        stderr_log: Path,
        stdout: str,
        stderr: str,
    ) -> None:
        stdout_log.write_text(stdout, encoding="utf-8")
        stderr_log.write_text(stderr, encoding="utf-8")
