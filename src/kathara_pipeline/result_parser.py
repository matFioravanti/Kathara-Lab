from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Iterable

from .exceptions import ReportParsingError
from .models import TestMetrics, VariantPaths
from .state_store import write_json_atomic


def _csv_files(root: Path) -> list[Path]:
    return sorted(
        [path for path in root.rglob("*.csv") if path.is_file()],
        key=lambda path: (len(path.parts), path.as_posix().casefold()),
    )


def _to_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        text = str(value).strip().replace("%", "")
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip().replace("%", ""))
    except (TypeError, ValueError):
        return None


def _normalize(row: dict[str, str]) -> dict[str, str]:
    return {str(k).strip().casefold().replace(" ", "_").replace("-", "_"): (v or "").strip() for k, v in row.items() if k is not None}


def _read_dict_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            sample = stream.read(4096)
            stream.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
            except csv.Error:
                dialect = csv.excel
            return [_normalize(dict(row)) for row in csv.DictReader(stream, dialect=dialect)]
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ReportParsingError(f"Cannot parse checker CSV {path}: {exc}") from exc


def _summary_metrics(rows: Iterable[dict[str, str]]) -> tuple[int, int, int, float] | None:
    aliases = {
        "total": ("total", "total_tests", "tests", "n_tests"),
        "passed": ("passed", "passed_tests", "success", "successes"),
        "failed": ("failed", "failed_tests", "failures", "failure"),
        "percentage": ("pass_percentage", "passed_percentage", "percentage", "score", "success_rate"),
    }
    for row in rows:
        total = next((v for k in aliases["total"] if (v := _to_int(row.get(k))) is not None), None)
        passed = next((v for k in aliases["passed"] if (v := _to_int(row.get(k))) is not None), None)
        failed = next((v for k in aliases["failed"] if (v := _to_int(row.get(k))) is not None), None)
        if passed is not None and failed is not None:
            if total is None:
                total = passed + failed
            pct = next((v for k in aliases["percentage"] if (v := _to_float(row.get(k))) is not None), None)
            if pct is None:
                pct = 100.0 if total == 0 else round(passed * 100.0 / total, 6)
            return total, passed, failed, pct
    return None


def _status_rows(rows: list[dict[str, str]]) -> tuple[int, int, int, dict[str, int]] | None:
    if not rows:
        return None
    status_keys = ("status", "result", "outcome", "test_result", "passed")
    category_keys = ("category", "check", "test", "type", "name")
    passed = failed = 0
    categories: dict[str, int] = {}
    recognized = 0
    for row in rows:
        raw = next((row.get(key) for key in status_keys if row.get(key) not in (None, "")), None)
        if raw is None:
            continue
        text = str(raw).strip().casefold()
        if text in {"passed", "pass", "ok", "true", "1", "success"}:
            passed += 1
            recognized += 1
        elif text in {"failed", "fail", "false", "0", "error", "ko"}:
            failed += 1
            recognized += 1
            category = next((row.get(key) for key in category_keys if row.get(key)), "uncategorized")
            categories[category] = categories.get(category, 0) + 1
    if not recognized:
        return None
    return recognized, passed, failed, categories


def parse_checker_results(paths: VariantPaths) -> TestMetrics:
    files = _csv_files(paths.checker_run)
    if not files:
        raise ReportParsingError("kathara-lab-checker completed without producing CSV reports")

    preferred = sorted(files, key=lambda p: ("summary" not in p.name.casefold(), "all" not in p.name.casefold(), p.name.casefold()))
    summary: tuple[int, int, int, float] | None = None
    categories: dict[str, int] = {}
    fallback: tuple[int, int, int, dict[str, int]] | None = None
    for path in preferred:
        rows = _read_dict_rows(path)
        if summary is None:
            summary = _summary_metrics(rows)
        status = _status_rows(rows)
        if status and (fallback is None or status[0] > fallback[0]):
            fallback = status
    if summary is not None:
        total, passed, failed, pct = summary
        if fallback and fallback[2] == failed:
            categories = fallback[3]
    elif fallback is not None:
        total, passed, failed, categories = fallback
        pct = 100.0 if total == 0 else round(passed * 100.0 / total, 6)
    else:
        # Last-resort support for a known checker summary JSON if future/current runtime emits it.
        json_summaries = list(paths.checker_run.rglob("*summary*.json"))
        parsed = None
        for candidate in json_summaries:
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(data, dict):
                p = _to_int(data.get("passed") or data.get("passed_tests"))
                f = _to_int(data.get("failed") or data.get("failed_tests"))
                if p is not None and f is not None:
                    t = _to_int(data.get("total") or data.get("total_tests")) or p + f
                    parsed = (t, p, f, 100.0 if t == 0 else round(p * 100.0 / t, 6))
                    break
        if parsed is None:
            raise ReportParsingError("CSV reports were found but no pass/fail metrics could be derived")
        total, passed, failed, pct = parsed

    paths.reports.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for source in files:
        target = paths.reports / source.name
        counter = 2
        while target.exists() and target.read_bytes() != source.read_bytes():
            target = paths.reports / f"{source.stem}-{counter}{source.suffix}"
            counter += 1
        if not target.exists():
            shutil.copy2(source, target)
        copied.append(target.name)

    metrics = TestMetrics(
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        pass_percentage=float(pct),
        failure_categories=categories,
        reports_found=tuple(copied),
    )
    write_json_atomic(paths.reports / "result-summary.json", metrics.to_dict())
    return metrics
