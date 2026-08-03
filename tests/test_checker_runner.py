from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from kathara_pipeline.checker_runner import CheckerRunner
from kathara_pipeline.exceptions import CheckerExecutionError
from kathara_pipeline.paths import build_job_paths


def _job(tmp_path: Path):
    paths = build_job_paths(tmp_path / "generated", "lab-1")
    paths.source.mkdir(parents=True)
    (paths.source / "lab.conf").write_text('r1[0]="A"\n', encoding="utf-8")
    (paths.source / "r1.startup").write_text("ip link set lo up\n", encoding="utf-8")
    paths.correction.parent.mkdir(parents=True)
    paths.correction.write_text(
        "default_image: kathara/base\nlab_inline: |\n  r1[0]=\"A\"\ntest: {}\n",
        encoding="utf-8",
    )
    paths.logs.mkdir(parents=True)
    return paths


def test_build_command_uses_current_interpreter_and_confirmed_flags(tmp_path: Path) -> None:
    command = CheckerRunner().build_command(
        correction_path=tmp_path / "correction.yaml",
        labs_directory=tmp_path / "labs",
    )
    assert command == [
        sys.executable,
        "-m",
        "kathara_lab_checker",
        "--config",
        str(tmp_path / "correction.yaml"),
        "--labs",
        str(tmp_path / "labs"),
        "--no-cache",
        "--report-type",
        "csv",
    ]


def test_checker_runner_cannot_disable_no_cache() -> None:
    with pytest.raises(ValueError, match="no-cache"):
        CheckerRunner(no_cache=False)


def test_run_copies_source_records_hashes_and_invokes_checker_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _job(tmp_path)
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="checker output", stderr="warning")

    monkeypatch.setattr("kathara_pipeline.checker_runner.subprocess.run", fake_run)
    result = CheckerRunner(timeout_seconds=21).run(paths)

    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[0] == sys.executable
    assert kwargs["shell"] is False
    assert kwargs["cwd"] == paths.checker_run
    assert kwargs["timeout"] == 21
    assert result.return_code == 0
    assert (paths.candidate / "lab.conf").read_text(encoding="utf-8") == 'r1[0]="A"\n'
    assert (paths.source / "lab.conf").read_text(encoding="utf-8") == 'r1[0]="A"\n'
    hashes = json.loads(
        (paths.checker_run / "copied-files.sha256.json").read_text(encoding="utf-8")
    )
    assert set(hashes["files"]) == {"lab.conf", "r1.startup"}
    assert (paths.logs / "checker.stdout.log").read_text(encoding="utf-8") == "checker output"
    assert (paths.logs / "checker.stderr.log").read_text(encoding="utf-8") == "warning"


def test_run_can_execute_an_explicitly_prepared_candidate_without_copying_twice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _job(tmp_path)
    runner = CheckerRunner()
    runner.prepare_candidate(paths)
    calls = 0

    def forbidden_prepare(_paths) -> dict[str, str]:
        raise AssertionError("candidate was prepared twice")

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(runner, "prepare_candidate", forbidden_prepare)
    monkeypatch.setattr("kathara_pipeline.checker_runner.subprocess.run", fake_run)

    result = runner.run(paths, prepared=True)

    assert result.return_code == 0
    assert calls == 1


def test_run_timeout_writes_partial_logs_and_does_not_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _job(tmp_path)
    calls = 0

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        raise subprocess.TimeoutExpired(
            command,
            timeout=2,
            output=b"partial stdout",
            stderr=b"partial stderr",
        )

    monkeypatch.setattr("kathara_pipeline.checker_runner.subprocess.run", fake_run)
    with pytest.raises(CheckerExecutionError, match="timed out") as captured:
        CheckerRunner(timeout_seconds=2).run(paths)
    assert calls == 1
    assert (paths.logs / "checker.stdout.log").read_text(encoding="utf-8") == "partial stdout"
    assert (paths.logs / "checker.stderr.log").read_text(encoding="utf-8") == "partial stderr"
    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["return_code"] is None
    assert metadata["timed_out"] is True
    assert metadata["cwd"] == str(paths.checker_run)
    assert metadata["stdout_log"] == str(paths.logs / "checker.stdout.log")
    assert metadata["stderr_log"] == str(paths.logs / "checker.stderr.log")


def test_nonzero_return_code_is_technical_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _job(tmp_path)

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 7, stdout="", stderr="daemon unavailable")

    monkeypatch.setattr("kathara_pipeline.checker_runner.subprocess.run", fake_run)
    with pytest.raises(CheckerExecutionError, match="return code 7") as captured:
        CheckerRunner().run(paths)
    assert "daemon unavailable" in (paths.logs / "checker.stderr.log").read_text(encoding="utf-8")
    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["return_code"] == 7
    assert metadata["timed_out"] is False
    assert metadata["command"][:3] == [sys.executable, "-m", "kathara_lab_checker"]


def test_external_source_symlink_is_rejected_before_checker_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = _job(tmp_path)
    external = tmp_path / "external.txt"
    external.write_text("secret", encoding="utf-8")
    (paths.source / "escape").symlink_to(external)
    called = False

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal called
        called = True
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("kathara_pipeline.checker_runner.subprocess.run", fake_run)
    with pytest.raises(CheckerExecutionError, match="safely"):
        CheckerRunner().run(paths)
    assert called is False
