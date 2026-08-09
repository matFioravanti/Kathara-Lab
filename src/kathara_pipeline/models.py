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
        return self in {self.PASSED, self.FAILED, self.ERROR, self.SKIPPED}


class Variant(str, Enum):
    WITH_SKILL = "with_skill"
    WITHOUT_SKILL = "without_skill"


class ComparisonOutcome(str, Enum):
    WITH_SKILL_BETTER = "WITH_SKILL_BETTER"
    WITHOUT_SKILL_BETTER = "WITHOUT_SKILL_BETTER"
    EQUAL = "EQUAL"
    INCOMPARABLE = "INCOMPARABLE"


@dataclass(frozen=True, slots=True)
class PromptRecord:
    path: Path
    name: str
    experiment_id: str
    content: str | None
    prompt_hash: str | None
    decode_error: str | None = None

    @property
    def empty(self) -> bool:
        return self.content is not None and not self.content.strip()


@dataclass(frozen=True, slots=True)
class ResourceFiles:
    root: Path
    creation_skill: Path
    checker_skill: Path
    checker_schema: Path
    creation_skill_hash: str
    checker_skill_hash: str
    checker_schema_hash: str


@dataclass(frozen=True, slots=True)
class CommandResult:
    command: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()
    data: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class TestMetrics:
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_percentage: float
    failure_categories: dict[str, int] = field(default_factory=dict)
    reports_found: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class VariantPaths:
    root: Path
    source: Path
    checker_run: Path
    labs_dir: Path
    candidate: Path
    reports: Path
    logs: Path
    manifest: Path
    workspace: Path
    correction_dir: Path
    correction: Path
    correction_logs: Path
    correction_workspace: Path


@dataclass(frozen=True, slots=True)
class ExperimentPaths:
    root: Path
    prompt: Path
    evaluation_spec: Path
    evaluation_spec_logs: Path
    evaluation_spec_workspace: Path
    comparison: Path
    comparison_csv: Path
    experiment_manifest: Path
    with_skill: VariantPaths
    without_skill: VariantPaths


@dataclass(slots=True)
class VariantSummary:
    experiment_id: str
    prompt_file: str
    variant: Variant
    status: JobStatus
    evaluation_spec_hash: str | None = None
    correction_generated: bool = False
    correction_hash: str | None = None
    lab_generated: bool = False
    static_validation_passed: bool = False
    checker_attempted: bool = False
    checker_completed: bool = False
    total_tests: int | None = None
    passed_tests: int | None = None
    failed_tests: int | None = None
    pass_percentage: float | None = None
    generation_duration_seconds: float | None = None
    checker_duration_seconds: float | None = None
    error_message: str | None = None
    skip_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["variant"] = self.variant.value
        data["status"] = self.status.value
        return data


@dataclass(slots=True)
class ExperimentSummary:
    experiment_id: str
    prompt_file: str
    evaluation_spec_generated: bool
    with_skill: VariantSummary
    without_skill: VariantSummary
    comparison: ComparisonOutcome
    comparison_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "prompt_file": self.prompt_file,
            "evaluation_spec_generated": self.evaluation_spec_generated,
            "with_skill": self.with_skill.to_dict(),
            "without_skill": self.without_skill.to_dict(),
            "comparison": self.comparison.value,
            "comparison_reason": self.comparison_reason,
        }


@dataclass(slots=True)
class PipelineSummary:
    pipeline_version: str
    started_at: str
    finished_at: str
    duration_seconds: float
    prompts_found: int
    experiments_completed: int
    variant_counts: dict[str, dict[str, int]]
    comparisons: dict[str, int]
    experiments: list[ExperimentSummary] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_version": self.pipeline_version,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "prompts_found": self.prompts_found,
            "experiments_completed": self.experiments_completed,
            "variant_counts": self.variant_counts,
            "comparisons": self.comparisons,
            "experiments": [item.to_dict() for item in self.experiments],
        }
