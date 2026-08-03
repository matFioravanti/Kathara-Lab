from __future__ import annotations

import json
from pathlib import Path

import pytest

from kathara_pipeline.exceptions import ReportParsingError
from kathara_pipeline.models import CheckerRunResult
from kathara_pipeline.paths import build_job_paths
from kathara_pipeline.result_parser import ResultParser


def _write_reports(
    tmp_path: Path,
    *,
    summary: tuple[int, int, int] = (3, 2, 1),
    include_failed: bool = True,
    aggregate: tuple[int, int, int] | None = (3, 2, 1),
):
    paths = build_job_paths(tmp_path / "generated", "lab-1")
    paths.candidate.mkdir(parents=True)
    total, passed, failed = summary
    (paths.candidate / "candidate_result_summary.csv").write_text(
        f"Total Tests,Passed Tests,Failed\n{total},{passed},{failed}\n",
        encoding="utf-8",
    )
    (paths.candidate / "candidate_result_all.csv").write_text(
        "Test Description,Passed,Reason\n"
        "Check existence of r1,True,OK\n"
        "Ping server,True,OK\n"
        "Check static route,False,Gateway is missing\n",
        encoding="utf-8",
    )
    if include_failed:
        (paths.candidate / "candidate_result_failed.csv").write_text(
            "Test Description,Passed,Reason\n"
            "Check static route,False,Gateway is missing\n",
            encoding="utf-8",
        )
    if aggregate is not None:
        agg_total, agg_passed, agg_failed = aggregate
        (paths.labs_dir / "results.csv").write_text(
            "Student Name,Tests Passed,Tests Failed,Tests Total Number,Problems\n"
            f"candidate,{agg_passed},{agg_failed},{agg_total},route failed\n",
            encoding="utf-8",
        )
    return paths


def test_parse_cross_checks_reports_and_classifies_legitimate_failures(
    tmp_path: Path,
) -> None:
    paths = _write_reports(tmp_path)
    metrics = ResultParser().parse(
        checker_run=paths.checker_run,
        labs_dir=paths.labs_dir,
        candidate=paths.candidate,
        checker_return_code=0,
    )

    assert metrics.total_tests == 3
    assert metrics.passed_tests == 2
    assert metrics.failed_tests == 1
    assert metrics.pass_percentage == pytest.approx(66.67)
    assert metrics.failure_categories == {"routing": 1}
    assert metrics.checker_execution_status == "completed"
    assert "labs/candidate/candidate_result_summary.csv" in metrics.reports_found
    # Failed tests are a valid checker outcome represented by metrics, not an exception.
    assert metrics.failed_tests > 0


def test_parse_and_store_copies_raw_reports_and_writes_summary(tmp_path: Path) -> None:
    paths = _write_reports(tmp_path)
    result = CheckerRunResult(
        command=("python", "-m", "kathara_lab_checker"),
        return_code=0,
        duration_seconds=1.5,
        stdout="",
        stderr="",
    )
    metrics = ResultParser().parse_and_store(paths, result)

    payload = json.loads(
        (paths.reports / "result-summary.json").read_text(encoding="utf-8")
    )
    assert metrics.failed_tests == 1
    assert payload["status"] == "failed"
    assert payload["checker_return_code"] == 0
    assert (
        paths.reports
        / "checker"
        / "labs"
        / "candidate"
        / "candidate_result_all.csv"
    ).is_file()
    assert (paths.reports / "checker" / "labs" / "results.csv").is_file()


def test_missing_required_report_is_a_technical_parsing_error(tmp_path: Path) -> None:
    paths = _write_reports(tmp_path, include_failed=False)
    with pytest.raises(ReportParsingError, match="missing") as caught:
        ResultParser().parse(
            checker_run=paths.checker_run,
            labs_dir=paths.labs_dir,
            candidate=paths.candidate,
            checker_return_code=0,
        )
    assert caught.value.details == ("failed",)


def test_parse_and_store_persists_structured_diagnostics_when_report_is_missing(
    tmp_path: Path,
) -> None:
    paths = _write_reports(tmp_path, include_failed=False)
    result = CheckerRunResult(
        command=("python", "-m", "kathara_lab_checker"),
        return_code=0,
        duration_seconds=0.75,
        stdout="",
        stderr="",
    )

    with pytest.raises(ReportParsingError, match="missing") as caught:
        ResultParser().parse_and_store(paths, result)

    payload = json.loads(
        (paths.reports / "result-summary.json").read_text(encoding="utf-8")
    )
    assert payload["status"] == "error"
    assert payload["checker_execution_status"] == "report_error"
    assert payload["reports_missing"] == ["failed"]
    assert "labs/candidate/candidate_result_summary.csv" in payload["reports_found"]
    assert payload["total_tests"] is None
    assert caught.value.report_diagnostics["reports_missing"] == ("failed",)


def test_parse_and_store_persists_malformed_report_as_found_but_missing_kind(
    tmp_path: Path,
) -> None:
    paths = _write_reports(tmp_path)
    malformed = paths.candidate / "candidate_result_summary.csv"
    malformed.write_text("Total Tests,Passed Tests,Failed\n3,2,1,extra\n", encoding="utf-8")
    result = CheckerRunResult(
        command=("python", "-m", "kathara_lab_checker"),
        return_code=0,
        duration_seconds=0.5,
        stdout="",
        stderr="",
    )

    with pytest.raises(ReportParsingError):
        ResultParser().parse_and_store(paths, result)

    payload = json.loads(
        (paths.reports / "result-summary.json").read_text(encoding="utf-8")
    )
    assert "labs/candidate/candidate_result_summary.csv" in payload["reports_found"]
    assert "summary" in payload["reports_missing"]
    assert "excess columns" in payload["error_message"]


def test_inconsistent_summary_is_a_technical_parsing_error(tmp_path: Path) -> None:
    paths = _write_reports(tmp_path, summary=(4, 3, 1), aggregate=None)
    with pytest.raises(ReportParsingError, match="disagree"):
        ResultParser().parse(
            checker_run=paths.checker_run,
            labs_dir=paths.labs_dir,
            candidate=paths.candidate,
            checker_return_code=0,
        )


def test_aggregate_counts_are_cross_checked_when_present(tmp_path: Path) -> None:
    paths = _write_reports(tmp_path, aggregate=(3, 1, 2))
    with pytest.raises(ReportParsingError, match="Aggregate"):
        ResultParser().parse(
            checker_run=paths.checker_run,
            labs_dir=paths.labs_dir,
            candidate=paths.candidate,
            checker_return_code=0,
        )


def test_nonzero_checker_process_is_error_not_failed_result(tmp_path: Path) -> None:
    paths = _write_reports(tmp_path)
    with pytest.raises(ReportParsingError, match="return code"):
        ResultParser().parse(
            checker_run=paths.checker_run,
            labs_dir=paths.labs_dir,
            candidate=paths.candidate,
            checker_return_code=9,
        )


def test_zero_executed_tests_is_not_a_vacuous_pass(tmp_path: Path) -> None:
    paths = _write_reports(tmp_path, summary=(0, 0, 0), aggregate=None)
    (paths.candidate / "candidate_result_all.csv").write_text(
        "Test Description,Passed,Reason\n", encoding="utf-8"
    )
    (paths.candidate / "candidate_result_failed.csv").write_text(
        "Test Description,Passed,Reason\n", encoding="utf-8"
    )

    with pytest.raises(ReportParsingError, match="zero executed tests"):
        ResultParser().parse(
            checker_run=paths.checker_run,
            labs_dir=paths.labs_dir,
            candidate=paths.candidate,
            checker_return_code=0,
        )
