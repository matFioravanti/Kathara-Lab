from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class JobStatus(str, Enum):
    DISCOVERED = "discovered"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"

    @property
    def terminal(self) -> bool:
        return self in {
            JobStatus.PASSED,
            JobStatus.FAILED,
            JobStatus.ERROR,
            JobStatus.SKIPPED,
        }


@dataclass(frozen=True, slots=True)
class PromptRecord:
    path: Path
    name: str
    lab_id: str
    content: str | None
    prompt_hash: str | None
    decode_error: str | None = None

    @property
    def empty(self) -> bool:
        return self.content is not None and not self.content.strip()


@dataclass(frozen=True, slots=True)
class ResourceFiles:
    root: Path
    skill_path: Path
    schema_path: Path
    examples_path: Path | None
    skill_hash: str
    schema_hash: str
    schema_mode: str


@dataclass(frozen=True, slots=True)
class JobPaths:
    root: Path
    prompt: Path
    source: Path
    correction_dir: Path
    correction: Path
    checker_run: Path
    labs_dir: Path
    candidate: Path
    reports: Path
    logs: Path
    manifest: Path
    lab_workspace: Path
    correction_workspace: Path


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False
    malformed_json_lines: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()
    mode: str | None = None
    data: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class CheckerRunResult:
    command: tuple[str, ...]
    return_code: int
    duration_seconds: float
    stdout: str
    stderr: str


@dataclass(frozen=True, slots=True)
class TestMetrics:
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_percentage: float
    failure_categories: dict[str, int]
    checker_process_return_code: int
    checker_execution_status: str
    reports_found: tuple[str, ...]
    reports_missing: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JobSummary:
    lab_id: str
    prompt_file: str
    status: JobStatus
    total_tests: int | None = None
    passed_tests: int | None = None
    failed_tests: int | None = None
    pass_percentage: float | None = None
    duration_seconds: float = 0.0
    error_message: str | None = None
    skip_reason: str | None = None
    lab_generated: bool = False
    checker_attempted: bool = False
    checker_completed: bool = False

    @property
    def lab_tested(self) -> bool:
        return self.checker_completed

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status.value
        result["lab_tested"] = self.lab_tested
        return result


@dataclass(slots=True)
class PipelineSummary:
    pipeline_version: str
    started_at: str
    finished_at: str
    duration_seconds: float
    prompts_found: int
    labs_generated: int
    checker_attempted: int
    checker_completed: int
    counts: dict[str, int]
    jobs: list[JobSummary] = field(default_factory=list)

    @property
    def labs_tested(self) -> int:
        return self.checker_completed

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_version": self.pipeline_version,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "prompts_found": self.prompts_found,
            "labs_generated": self.labs_generated,
            "checker_attempted": self.checker_attempted,
            "checker_completed": self.checker_completed,
            "labs_tested": self.labs_tested,
            "counts": self.counts,
            "jobs": [job.to_dict() for job in self.jobs],
        }

