from __future__ import annotations

import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ReportParsingError
from .models import CheckerRunResult, JobPaths, TestMetrics
from .paths import safe_rmtree
from .state_store import write_json_atomic


def _normalise_header(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def _parse_nonnegative_int(value: str | None, *, field: str, path: Path) -> int:
    try:
        number = int((value or "").strip())
    except ValueError as exc:
        raise ReportParsingError(f"Invalid integer in {path.name}: {field}={value!r}") from exc
    if number < 0:
        raise ReportParsingError(f"Negative count in {path.name}: {field}={number}")
    return number


def _parse_bool(value: str | None, *, path: Path) -> bool:
    normalised = (value or "").strip().casefold()
    if normalised in {"true", "yes", "1", "passed", "pass"}:
        return True
    if normalised in {"false", "no", "0", "failed", "fail"}:
        return False
    raise ReportParsingError(f"Invalid Passed value in {path.name}: {value!r}")


@dataclass(frozen=True, slots=True)
class _CsvReport:
    path: Path
    kind: str
    rows: tuple[dict[str, str], ...]


class ResultParser:
    """Classify and cross-check CSV reports produced by kathara-lab-checker."""

    _AGGREGATE_COLUMNS = {
        "student name",
        "tests passed",
        "tests failed",
        "tests total number",
    }
    _SUMMARY_BASE_COLUMNS = {"total tests", "passed tests"}
    _DETAIL_COLUMNS = {"test description", "passed", "reason"}

    def parse(
        self,
        *,
        checker_run: Path,
        labs_dir: Path,
        candidate: Path,
        checker_return_code: int,
    ) -> TestMetrics:
        if checker_return_code != 0:
            raise ReportParsingError(
                f"Cannot classify reports from checker return code {checker_return_code}"
            )
        reports = self._discover_reports(labs_dir)
        if not reports:
            raise ReportParsingError("No readable checker CSV reports were found")

        summary = self._choose_candidate_report(reports, "summary", candidate)
        all_results = self._choose_candidate_report(reports, "all", candidate)
        failed_results = self._choose_candidate_report(reports, "failed", candidate)
        missing = tuple(
            name
            for name, report in (
                ("summary", summary),
                ("all", all_results),
                ("failed", failed_results),
            )
            if report is None
        )
        if missing:
            raise ReportParsingError(
                "Required checker reports are missing",
                details=missing,
            )
        assert summary is not None and all_results is not None and failed_results is not None

        total, passed, failed = self._summary_counts(summary)
        if total == 0:
            raise ReportParsingError("Checker reports contain zero executed tests")
        all_total, all_passed, all_failed = self._detail_counts(all_results)
        failed_rows_total, failed_rows_passed, failed_rows_failed = self._detail_counts(
            failed_results
        )
        if (total, passed, failed) != (all_total, all_passed, all_failed):
            raise ReportParsingError(
                "Summary and all-results CSV counts disagree",
                details=(
                    f"summary={(total, passed, failed)}",
                    f"all={(all_total, all_passed, all_failed)}",
                ),
            )
        if failed_rows_passed or failed_rows_total != failed or failed_rows_failed != failed:
            raise ReportParsingError(
                "Failed-results CSV does not match the authoritative failure count",
                details=(
                    f"expected_failed={failed}",
                    f"failed_report={(failed_rows_total, failed_rows_passed, failed_rows_failed)}",
                ),
            )

        aggregate_reports = [report for report in reports if report.kind == "aggregate"]
        for aggregate in aggregate_reports:
            aggregate_counts = self._aggregate_counts(aggregate, candidate.name)
            if aggregate_counts != (total, passed, failed):
                raise ReportParsingError(
                    f"Aggregate report {aggregate.path.name} disagrees with per-lab reports",
                    details=(
                        f"per_lab={(total, passed, failed)}",
                        f"aggregate={aggregate_counts}",
                    ),
                )

        categories = self._failure_categories(failed_results.rows)
        pass_percentage = round((passed / total * 100.0) if total else 100.0, 2)
        reports_found = tuple(
            self._display_path(report.path, checker_run)
            for report in sorted(reports, key=lambda item: item.path.as_posix())
        )
        return TestMetrics(
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            pass_percentage=pass_percentage,
            failure_categories=categories,
            checker_process_return_code=checker_return_code,
            checker_execution_status="completed",
            reports_found=reports_found,
            reports_missing=(),
        )

    def parse_and_store(
        self,
        job_paths: JobPaths,
        checker_result: CheckerRunResult,
    ) -> TestMetrics:
        """Preserve raw CSVs, parse them, and atomically write the job summary."""

        self._copy_raw_reports(job_paths)
        try:
            metrics = self.parse(
                checker_run=job_paths.checker_run,
                labs_dir=job_paths.labs_dir,
                candidate=job_paths.candidate,
                checker_return_code=checker_result.return_code,
            )
        except ReportParsingError as exc:
            reports_found, reports_missing = self.report_inventory(job_paths)
            details = "; ".join(str(item) for item in exc.details)
            error_message = f"{exc}: {details}" if details else str(exc)
            diagnostics = {
                "total_tests": None,
                "passed_tests": None,
                "failed_tests": None,
                "pass_percentage": None,
                "failure_categories": {},
                "checker_process_return_code": checker_result.return_code,
                "checker_execution_status": "report_error",
                "reports_found": reports_found,
                "reports_missing": reports_missing,
            }
            payload = {
                "lab_id": job_paths.root.name,
                "status": "error",
                **diagnostics,
                "checker_return_code": checker_result.return_code,
                "checker_duration_seconds": checker_result.duration_seconds,
                "checker_command": list(checker_result.command),
                "checker_working_directory": str(job_paths.checker_run),
                "error_message": error_message,
            }
            job_paths.reports.mkdir(parents=True, exist_ok=True)
            write_json_atomic(job_paths.reports / "result-summary.json", payload)
            exc.report_diagnostics = diagnostics
            raise
        status = "failed" if metrics.failed_tests else "passed"
        payload = {
            "lab_id": job_paths.root.name,
            "status": status,
            **metrics.to_dict(),
            "checker_return_code": checker_result.return_code,
        }
        job_paths.reports.mkdir(parents=True, exist_ok=True)
        write_json_atomic(job_paths.reports / "result-summary.json", payload)
        return metrics

    def report_inventory(
        self,
        job_paths: JobPaths,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Describe raw CSV presence without masking the original parse error."""

        required = {"summary", "all", "failed"}
        recognized: set[str] = set()
        found: list[str] = []
        if not job_paths.labs_dir.is_dir():
            return (), tuple(sorted(required))

        candidate = job_paths.candidate.resolve(strict=False)
        for path in sorted(job_paths.labs_dir.rglob("*.csv"), key=lambda item: item.as_posix()):
            if not path.is_file() or path.is_symlink():
                continue
            found.append(self._display_path(path, job_paths.checker_run))
            if not path.resolve(strict=False).is_relative_to(candidate):
                continue
            try:
                headers, rows = self._read_csv(path)
                kind = self._classify(path, headers, rows)
            except ReportParsingError:
                continue
            if kind in required:
                recognized.add(kind)
        return tuple(found), tuple(sorted(required - recognized))

    def _discover_reports(self, labs_dir: Path) -> list[_CsvReport]:
        if not labs_dir.is_dir():
            raise ReportParsingError(f"Checker labs directory is missing: {labs_dir}")
        discovered: list[_CsvReport] = []
        for path in sorted(labs_dir.rglob("*.csv"), key=lambda item: item.as_posix()):
            if not path.is_file() or path.is_symlink():
                continue
            try:
                headers, rows = self._read_csv(path)
            except ReportParsingError:
                if self._report_like_name(path):
                    raise
                continue
            kind = self._classify(path, headers, rows)
            if kind is not None:
                discovered.append(_CsvReport(path=path, kind=kind, rows=rows))
        return discovered

    @staticmethod
    def _read_csv(path: Path) -> tuple[set[str], tuple[dict[str, str], ...]]:
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                if reader.fieldnames is None:
                    raise ReportParsingError(f"CSV report has no header: {path}")
                normalised = [_normalise_header(header or "") for header in reader.fieldnames]
                if any(not header for header in normalised) or len(set(normalised)) != len(normalised):
                    raise ReportParsingError(f"CSV report has invalid or duplicate headers: {path}")
                rows: list[dict[str, str]] = []
                for raw_row in reader:
                    if None in raw_row:
                        raise ReportParsingError(f"CSV row has excess columns: {path}")
                    row = {
                        _normalise_header(key): (value or "").strip()
                        for key, value in raw_row.items()
                    }
                    if any(value for value in row.values()):
                        rows.append(row)
        except (OSError, UnicodeError, csv.Error) as exc:
            raise ReportParsingError(f"Cannot read checker CSV report {path}: {exc}") from exc
        return set(normalised), tuple(rows)

    @classmethod
    def _classify(
        cls,
        path: Path,
        headers: set[str],
        rows: tuple[dict[str, str], ...],
    ) -> str | None:
        if cls._AGGREGATE_COLUMNS.issubset(headers):
            return "aggregate"
        failed_key = "failed" if "failed" in headers else "failed tests"
        if cls._SUMMARY_BASE_COLUMNS.issubset(headers) and failed_key in headers:
            return "summary"
        if cls._DETAIL_COLUMNS.issubset(headers):
            tokens = set(_normalise_header(path.stem).split())
            if "failed" in tokens:
                return "failed"
            if "all" in tokens:
                return "all"
            if rows and all(not _parse_bool(row.get("passed"), path=path) for row in rows):
                return "failed"
        return None

    @staticmethod
    def _report_like_name(path: Path) -> bool:
        tokens = set(_normalise_header(path.stem).split())
        return bool(tokens & {"result", "results", "summary", "failed", "report"})

    @staticmethod
    def _choose_candidate_report(
        reports: list[_CsvReport],
        kind: str,
        candidate: Path,
    ) -> _CsvReport | None:
        candidates = [
            report
            for report in reports
            if report.kind == kind and report.path.resolve().is_relative_to(candidate.resolve())
        ]
        if not candidates:
            return None

        def score(report: _CsvReport) -> tuple[int, int, int]:
            tokens = set(_normalise_header(report.path.stem).split())
            return (
                int(report.path.parent.resolve() == candidate.resolve()),
                int(candidate.name.casefold() in report.path.stem.casefold()),
                int(kind in tokens),
            )

        ranked = sorted(candidates, key=lambda report: (score(report), report.path.as_posix()), reverse=True)
        best_score = score(ranked[0])
        tied = [report for report in ranked if score(report) == best_score]
        if len(tied) > 1:
            raise ReportParsingError(
                f"Ambiguous {kind} checker reports",
                details=tuple(str(report.path) for report in tied),
            )
        return ranked[0]

    @staticmethod
    def _summary_counts(report: _CsvReport) -> tuple[int, int, int]:
        if len(report.rows) != 1:
            raise ReportParsingError(
                f"Summary report must contain exactly one data row: {report.path}"
            )
        row = report.rows[0]
        failed_field = "failed" if "failed" in row else "failed tests"
        total = _parse_nonnegative_int(row.get("total tests"), field="Total Tests", path=report.path)
        passed = _parse_nonnegative_int(row.get("passed tests"), field="Passed Tests", path=report.path)
        failed = _parse_nonnegative_int(row.get(failed_field), field="Failed", path=report.path)
        if total != passed + failed:
            raise ReportParsingError(
                f"Inconsistent counts in summary report {report.path.name}",
                details=(f"total={total}, passed={passed}, failed={failed}",),
            )
        return total, passed, failed

    @staticmethod
    def _detail_counts(report: _CsvReport) -> tuple[int, int, int]:
        passed = sum(_parse_bool(row.get("passed"), path=report.path) for row in report.rows)
        total = len(report.rows)
        return total, passed, total - passed

    @staticmethod
    def _aggregate_counts(report: _CsvReport, candidate_name: str) -> tuple[int, int, int]:
        matching = [
            row
            for row in report.rows
            if row.get("student name", "").strip().casefold() == candidate_name.casefold()
        ]
        if len(matching) != 1:
            raise ReportParsingError(
                f"Aggregate report must contain exactly one row for {candidate_name}",
                details=(str(report.path),),
            )
        row = matching[0]
        total = _parse_nonnegative_int(
            row.get("tests total number"), field="Tests Total Number", path=report.path
        )
        passed = _parse_nonnegative_int(
            row.get("tests passed"), field="Tests Passed", path=report.path
        )
        failed = _parse_nonnegative_int(
            row.get("tests failed"), field="Tests Failed", path=report.path
        )
        if total != passed + failed:
            raise ReportParsingError(f"Inconsistent aggregate counts in {report.path.name}")
        return total, passed, failed

    @classmethod
    def _failure_categories(cls, rows: tuple[dict[str, str], ...]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            text = f"{row.get('test description', '')} {row.get('reason', '')}".casefold()
            category = cls._categorise_failure(text)
            counts[category] = counts.get(category, 0) + 1
        return dict(sorted(counts.items()))

    @staticmethod
    def _categorise_failure(text: str) -> str:
        categories = (
            ("dns", ("dns", "name server", "nameserver", "resolver", "domain record")),
            ("http", ("http", "https", "web server", "curl")),
            ("routing", ("route", "routing", "gateway", "next hop", "ospf", "bgp", "rip")),
            ("reachability", ("reachab", "ping", "unreachable", "cannot reach")),
            ("startup", ("startup",)),
            ("service", ("daemon", "service", "process", "listening", "port ")),
            ("topology", ("existence", "collision domain", "interface", "device")),
            ("configuration", ("sysctl", "configuration", "configured")),
        )
        for category, markers in categories:
            if any(marker in text for marker in markers):
                return category
        return "other"

    @staticmethod
    def _display_path(path: Path, root: Path) -> str:
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return str(path)

    @staticmethod
    def _copy_raw_reports(job_paths: JobPaths) -> None:
        raw_root = job_paths.reports / "checker"
        if raw_root.exists() or raw_root.is_symlink():
            safe_rmtree(raw_root, job_paths.root.parent)
        raw_root.mkdir(parents=True, exist_ok=True)
        for source in sorted(job_paths.checker_run.rglob("*.csv"), key=lambda item: item.as_posix()):
            if not source.is_file() or source.is_symlink():
                continue
            relative = source.relative_to(job_paths.checker_run)
            destination = raw_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
