from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .models import ComparisonOutcome, ExperimentSummary, JobStatus, VariantSummary
from .state_store import write_json_atomic


def compare_variants(with_skill: VariantSummary, without_skill: VariantSummary) -> tuple[ComparisonOutcome, str]:
    if not with_skill.checker_completed or not without_skill.checker_completed:
        return ComparisonOutcome.INCOMPARABLE, "Both checker runs must complete successfully for a paired quality comparison."
    if with_skill.total_tests is None or without_skill.total_tests is None:
        return ComparisonOutcome.INCOMPARABLE, "Missing checker metrics."
    if with_skill.total_tests != without_skill.total_tests:
        return ComparisonOutcome.INCOMPARABLE, "Per-variant corrections produced different test counts; pair excluded from quality comparison."
    if with_skill.failed_tests is None or without_skill.failed_tests is None:
        return ComparisonOutcome.INCOMPARABLE, "Missing failed-test counts."
    if with_skill.failed_tests < without_skill.failed_tests:
        return ComparisonOutcome.WITH_SKILL_BETTER, "With-skill candidate failed fewer checks."
    if without_skill.failed_tests < with_skill.failed_tests:
        return ComparisonOutcome.WITHOUT_SKILL_BETTER, "Without-skill candidate failed fewer checks."
    return ComparisonOutcome.EQUAL, "Both candidates produced the same checker result."


def comparison_payload(summary: ExperimentSummary) -> dict[str, Any]:
    a = summary.with_skill
    b = summary.without_skill
    return {
        "experiment_id": summary.experiment_id,
        "prompt_file": summary.prompt_file,
        "evaluation_spec_sha256": a.evaluation_spec_hash or b.evaluation_spec_hash,
        "outcome": summary.comparison.value,
        "reason": summary.comparison_reason,
        "with_skill": a.to_dict(),
        "without_skill": b.to_dict(),
        "delta": {
            "passed_tests": (a.passed_tests - b.passed_tests) if a.passed_tests is not None and b.passed_tests is not None else None,
            "failed_tests": (a.failed_tests - b.failed_tests) if a.failed_tests is not None and b.failed_tests is not None else None,
            "pass_percentage_points": round(a.pass_percentage - b.pass_percentage, 6) if a.pass_percentage is not None and b.pass_percentage is not None else None,
            "generation_duration_seconds": round(a.generation_duration_seconds - b.generation_duration_seconds, 6) if a.generation_duration_seconds is not None and b.generation_duration_seconds is not None else None,
            "checker_duration_seconds": round(a.checker_duration_seconds - b.checker_duration_seconds, 6) if a.checker_duration_seconds is not None and b.checker_duration_seconds is not None else None,
        },
    }


def write_comparison(summary: ExperimentSummary, json_path: Path, csv_path: Path) -> None:
    payload = comparison_payload(summary)
    write_json_atomic(json_path, payload)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "experiment_id": summary.experiment_id,
        "prompt_file": summary.prompt_file,
        "outcome": summary.comparison.value,
        "reason": summary.comparison_reason or "",
        "evaluation_spec_sha256": summary.with_skill.evaluation_spec_hash or summary.without_skill.evaluation_spec_hash or "",
        "with_skill_status": summary.with_skill.status.value,
        "without_skill_status": summary.without_skill.status.value,
        "with_skill_pass_percentage": summary.with_skill.pass_percentage if summary.with_skill.pass_percentage is not None else "",
        "without_skill_pass_percentage": summary.without_skill.pass_percentage if summary.without_skill.pass_percentage is not None else "",
        "delta_pass_percentage_points": payload["delta"]["pass_percentage_points"] if payload["delta"]["pass_percentage_points"] is not None else "",
        "with_skill_failed_tests": summary.with_skill.failed_tests if summary.with_skill.failed_tests is not None else "",
        "without_skill_failed_tests": summary.without_skill.failed_tests if summary.without_skill.failed_tests is not None else "",
    }
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
