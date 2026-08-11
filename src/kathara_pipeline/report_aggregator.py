from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path
from typing import Any

from .models import ComparisonOutcome, ExperimentSummary, JobStatus, PipelineSummary, Variant
from .state_store import write_json_atomic


def _mean(values: list[float]) -> float | None:
    return round(statistics.fmean(values), 6) if values else None


def _median(values: list[float]) -> float | None:
    return round(statistics.median(values), 6) if values else None


def aggregate_payload(experiments: list[ExperimentSummary]) -> dict[str, Any]:
    def variant_values(name: str):
        return [getattr(item, name) for item in experiments]

    with_items = variant_values("with_skill")
    without_items = variant_values("without_skill")

    def status_counts(items):
        return {status.value: sum(1 for item in items if item.status is status) for status in (JobStatus.PASSED, JobStatus.FAILED, JobStatus.ERROR, JobStatus.SKIPPED)}

    comparable = [item for item in experiments if item.comparison is not ComparisonOutcome.INCOMPARABLE]
    deltas = [
        item.with_skill.pass_percentage - item.without_skill.pass_percentage
        for item in comparable
        if item.with_skill.pass_percentage is not None and item.without_skill.pass_percentage is not None
    ]
    outcomes = {outcome.value: sum(1 for item in experiments if item.comparison is outcome) for outcome in ComparisonOutcome}
    return {
        "total_prompts": len(experiments),
        "comparable_pairs": len(comparable),
        "incomparable_pairs": outcomes[ComparisonOutcome.INCOMPARABLE.value],
        "quality": {
            "with_skill": {
                "status_counts": status_counts(with_items),
                "mean_pass_percentage": _mean([float(i.pass_percentage) for i in with_items if i.pass_percentage is not None]),
                "median_pass_percentage": _median([float(i.pass_percentage) for i in with_items if i.pass_percentage is not None]),
            },
            "without_skill": {
                "status_counts": status_counts(without_items),
                "mean_pass_percentage": _mean([float(i.pass_percentage) for i in without_items if i.pass_percentage is not None]),
                "median_pass_percentage": _median([float(i.pass_percentage) for i in without_items if i.pass_percentage is not None]),
            },
            "paired": {
                "outcomes": outcomes,
                "mean_delta_pass_percentage_points": _mean([float(v) for v in deltas]),
                "median_delta_pass_percentage_points": _median([float(v) for v in deltas]),
            },
        },
        "technical_reliability": {
            "with_skill_checker_completion_rate": round(sum(i.checker_completed for i in with_items) * 100.0 / len(with_items), 6) if with_items else None,
            "without_skill_checker_completion_rate": round(sum(i.checker_completed for i in without_items) * 100.0 / len(without_items), 6) if without_items else None,
            "with_skill_errors": sum(i.status is JobStatus.ERROR for i in with_items),
            "without_skill_errors": sum(i.status is JobStatus.ERROR for i in without_items),
        },
        "time": {
            "with_skill_mean_generation_seconds": _mean([float(i.lab_duration_seconds) for i in with_items if i.lab_duration_seconds is not None]),
            "without_skill_mean_generation_seconds": _mean([float(i.lab_duration_seconds) for i in without_items if i.lab_duration_seconds is not None]),
            "with_skill_mean_checker_seconds": _mean([float(i.checker_duration_seconds) for i in with_items if i.checker_duration_seconds is not None]),
            "without_skill_mean_checker_seconds": _mean([float(i.checker_duration_seconds) for i in without_items if i.checker_duration_seconds is not None]),
        },
    }


def write_aggregate(output_root: Path, experiments: list[ExperimentSummary]) -> dict[str, Any]:
    summary_dir = output_root / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    payload = aggregate_payload(experiments)
    write_json_atomic(summary_dir / "aggregate.json", payload)

    rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    for experiment in experiments:
        for variant_name, item in (("with_skill", experiment.with_skill), ("without_skill", experiment.without_skill)):
            rows.append({
                "experiment_id": experiment.experiment_id,
                "prompt_file": experiment.prompt_file,
                "variant": variant_name,
                "status": item.status.value,
                "checker_completed": item.checker_completed,
                "total_tests": item.total_tests if item.total_tests is not None else "",
                "passed_tests": item.passed_tests if item.passed_tests is not None else "",
                "failed_tests": item.failed_tests if item.failed_tests is not None else "",
                "pass_percentage": item.pass_percentage if item.pass_percentage is not None else "",
                "generation_duration_seconds": item.lab_duration_seconds if item.lab_duration_seconds is not None else "",
                "checker_duration_seconds": item.checker_duration_seconds if item.checker_duration_seconds is not None else "",
                "correction_sha256": item.correction_hash or "",
                "error": item.error_message or "",
            })
        a, b = experiment.with_skill, experiment.without_skill
        pair_rows.append({
            "experiment_id": experiment.experiment_id,
            "prompt_file": experiment.prompt_file,
            "outcome": experiment.comparison.value,
            "reason": experiment.comparison_reason or "",
            "with_skill_pass_percentage": a.pass_percentage if a.pass_percentage is not None else "",
            "without_skill_pass_percentage": b.pass_percentage if b.pass_percentage is not None else "",
            "delta_pass_percentage_points": round(a.pass_percentage - b.pass_percentage, 6) if a.pass_percentage is not None and b.pass_percentage is not None else "",
        })

    def write_csv(path: Path, data: list[dict[str, Any]]) -> None:
        if not data:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)

    write_csv(summary_dir / "experiments.csv", rows)
    write_csv(summary_dir / "pair-comparisons.csv", pair_rows)

    flat = {
        "total_prompts": payload["total_prompts"],
        "comparable_pairs": payload["comparable_pairs"],
        "incomparable_pairs": payload["incomparable_pairs"],
        "with_skill_better": payload["quality"]["paired"]["outcomes"][ComparisonOutcome.WITH_SKILL_BETTER.value],
        "without_skill_better": payload["quality"]["paired"]["outcomes"][ComparisonOutcome.WITHOUT_SKILL_BETTER.value],
        "equal": payload["quality"]["paired"]["outcomes"][ComparisonOutcome.EQUAL.value],
        "mean_delta_pass_percentage_points": payload["quality"]["paired"]["mean_delta_pass_percentage_points"],
    }
    write_csv(summary_dir / "aggregate.csv", [flat])
    return payload
