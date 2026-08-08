from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

from .exceptions import CheckerExecutionError
from .models import CommandResult, VariantPaths


class CheckerRunner:
    def __init__(self, *, timeout_seconds: int = 1800, no_cache: bool = True, report_type: str = "csv"):
        self.timeout_seconds = timeout_seconds
        self.no_cache = no_cache
        self.report_type = report_type

    def prepare_candidate(self, source: Path, paths: VariantPaths) -> None:
        if paths.checker_run.exists():
            shutil.rmtree(paths.checker_run)
        paths.labs_dir.mkdir(parents=True)
        shutil.copytree(source, paths.candidate, symlinks=True)

    def build_command(self, *, correction: Path, paths: VariantPaths) -> tuple[str, ...]:
        args = [
            sys.executable,
            "-m",
            "kathara_lab_checker",
            "--config",
            str(correction),
            "--labs",
            str(paths.labs_dir),
        ]
        if self.no_cache:
            args.append("--no-cache")
        args += ["--report-type", self.report_type]
        return tuple(args)

    def run(self, *, correction: Path, paths: VariantPaths) -> CommandResult:
        paths.logs.mkdir(parents=True, exist_ok=True)
        command = self.build_command(correction=correction, paths=paths)
        start = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=paths.checker_run,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            result = CommandResult(
                command=command,
                return_code=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                duration_seconds=time.monotonic() - start,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            result = CommandResult(
                command=command,
                return_code=124,
                stdout=exc.stdout if isinstance(exc.stdout, str) else "",
                stderr=(exc.stderr if isinstance(exc.stderr, str) else "") + "\nchecker timeout\n",
                duration_seconds=time.monotonic() - start,
                timed_out=True,
            )
        (paths.logs / "checker.stdout.log").write_text(result.stdout, encoding="utf-8")
        (paths.logs / "checker.stderr.log").write_text(result.stderr, encoding="utf-8")
        if result.timed_out:
            raise CheckerExecutionError(f"kathara-lab-checker timed out after {self.timeout_seconds}s")
        # The checker may use a non-zero status for failed tests in some versions. Parsing the
        # produced CSV is authoritative when report artifacts exist; a non-zero code without
        # any CSV is treated as a technical execution error by the pipeline/result parser.
        return result
