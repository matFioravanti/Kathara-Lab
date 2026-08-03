from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from kathara_pipeline import __version__
from kathara_pipeline.config import load_config
from kathara_pipeline.exceptions import (
    CheckerExecutionError,
    CodexExecutionError,
    PreflightError,
)
from kathara_pipeline.models import (
    CheckerRunResult,
    JobStatus,
    JobSummary,
    PromptRecord,
    ResourceFiles,
    TestMetrics as Metrics,
    ValidationResult,
)
from kathara_pipeline.paths import build_job_paths
from kathara_pipeline.paths import ensure_generated_root_managed
from kathara_pipeline.pipeline import Pipeline
from kathara_pipeline.preflight import PreflightReport
from kathara_pipeline.state_store import sha256_file, sha256_text, write_json_atomic


def _config(tmp_path: Path, *, continue_on_error: bool = True):
    (tmp_path / "prompts_generates").mkdir()
    checker = tmp_path / "kathara-lab-checker"
    checker.mkdir()
    (checker / "SKILL.md").write_text("skill", encoding="utf-8")
    (checker / "config-schema.md").write_text("schema", encoding="utf-8")
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        "processing:\n"
        f"  continue_on_error: {'true' if continue_on_error else 'false'}\n",
        encoding="utf-8",
    )
    return load_config(config_path)


def _resources(tmp_path: Path) -> ResourceFiles:
    root = tmp_path / "kathara-lab-checker"
    skill = root / "SKILL.md"
    schema = root / "config-schema.md"
    return ResourceFiles(
        root=root,
        skill_path=skill,
        schema_path=schema,
        examples_path=None,
        skill_hash=sha256_file(skill),
        schema_hash=sha256_file(schema),
        schema_mode="documented-structure",
    )


def _prompt(tmp_path: Path, name: str = "lab-1.md") -> PromptRecord:
    path = tmp_path / "prompts_generates" / name
    content = "Build one router."
    path.write_text(content, encoding="utf-8")
    return PromptRecord(path, name, Path(name).stem, content, sha256_text(content))


def test_single_job_invokes_each_external_phase_once_and_traces_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    pipeline = Pipeline(config, emit=lambda _message: None)
    calls = {"lab": 0, "correction": 0, "checker": 0, "parser": 0, "yaml": 0}

    class LabGenerator:
        @staticmethod
        def _instruction() -> str:
            return "generate lab"

        def generate(self, _prompt: PromptRecord, paths):
            calls["lab"] += 1
            paths.source.mkdir(parents=True)
            (paths.source / "lab.conf").write_text('r1[0]="lan"\n', encoding="utf-8")
            (paths.source / "r1.startup").write_text(
                "ip addr add 10.0.0.1/24 dev eth0\n", encoding="utf-8"
            )
            from kathara_pipeline.models import CommandResult

            return CommandResult(("codex", "exec", "lab instruction"), 0, "", "", 0.1)

    class CorrectionGenerator:
        @staticmethod
        def _instruction(**_kwargs: Any) -> str:
            return "generate correction"

        def generate(self, _prompt: PromptRecord, paths, _resources: ResourceFiles):
            calls["correction"] += 1
            paths.correction.write_text("test: {}\n", encoding="utf-8")
            from kathara_pipeline.models import CommandResult

            return CommandResult(
                ("codex", "exec", "correction instruction"), 0, "", "", 0.2
            )

    class Checker:
        def prepare_candidate(self, paths) -> dict[str, str]:
            paths.candidate.mkdir(parents=True)
            return {"lab.conf": "hash"}

        def build_command(self, **_kwargs: Any) -> list[str]:
            return ["checker"]

        def run(self, _paths, *, prepared: bool = False) -> CheckerRunResult:
            assert prepared
            calls["checker"] += 1
            return CheckerRunResult(("checker",), 0, 0.01, "", "")

    class Parser:
        def parse_and_store(self, paths, _result) -> Metrics:
            calls["parser"] += 1
            (paths.reports / "candidate_result_all.csv").write_text(
                "Test Description,Passed,Reason\nexists,True,OK\n", encoding="utf-8"
            )
            return Metrics(1, 1, 0, 100.0, {}, 0, "completed", ("all.csv",), ())

    class Validator:
        def __init__(self, _schema: Path, _skill: Path | None = None) -> None:
            pass

        def validate(self, _correction: Path, _lab: Path, _job: Path) -> ValidationResult:
            calls["yaml"] += 1
            return ValidationResult(True, mode="documented-structural", data={"test": {}})

    pipeline.lab_generator = LabGenerator()  # type: ignore[assignment]
    pipeline.correction_generator = CorrectionGenerator()  # type: ignore[assignment]
    pipeline.checker_runner = Checker()  # type: ignore[assignment]
    pipeline.result_parser = Parser()  # type: ignore[assignment]
    monkeypatch.setattr("kathara_pipeline.pipeline.YamlValidator", Validator)

    outcome = pipeline.process_single_prompt(prompt, resources, force=False)

    assert outcome.status is JobStatus.PASSED
    assert calls == {"lab": 1, "correction": 1, "checker": 1, "parser": 1, "yaml": 1}
    manifest = json.loads(
        build_job_paths(config.paths.generated_labs, prompt.lab_id).manifest.read_text(encoding="utf-8")
    )
    phases = [phase["name"] for phase in manifest["phases"]]
    expected_order = [
        "discovered",
        "job_created",
        "lab_generated",
        "lab_validated",
        "correction_generated",
        "correction_validated",
        "checker_prepared",
        "checker_executed",
        "reports_parsed",
        "result_saved",
        "manifest_updated",
        "completed",
    ]
    positions = [phases.index(name) for name in expected_order]
    assert positions == sorted(positions)
    assert manifest["codex_lab"]["command"][-1] == "<instruction>"
    assert manifest["codex_correction"]["duration_seconds"] == pytest.approx(0.2)
    assert manifest["checker_process"]["working_directory"].endswith("checker-run")


@pytest.mark.parametrize(
    ("failing_phase", "manifest_field", "error_type"),
    [
        ("lab", "codex_lab", CodexExecutionError),
        ("correction", "codex_correction", CodexExecutionError),
        ("checker", "checker_process", CheckerExecutionError),
    ],
)
def test_process_error_metadata_is_persisted_for_the_active_phase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failing_phase: str,
    manifest_field: str,
    error_type: type[Exception],
) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    pipeline = Pipeline(config, emit=lambda _message: None)
    metadata = {
        "command": ["tool", "exec", "<instruction>"],
        "return_code": None,
        "duration_seconds": 1.25,
        "timed_out": True,
        "cwd": "/work",
        "stderr_log": "/work/error.log",
    }

    class LabGenerator:
        @staticmethod
        def _instruction() -> str:
            return "generate lab"

        def generate(self, _prompt: PromptRecord, paths):
            if failing_phase == "lab":
                raise error_type("process failed", process_metadata=metadata)
            paths.source.mkdir(parents=True)
            (paths.source / "lab.conf").write_text('r1[0]="lan"\n', encoding="utf-8")
            (paths.source / "r1.startup").write_text("ip link set lo up\n", encoding="utf-8")
            from kathara_pipeline.models import CommandResult

            return CommandResult(("codex", "exec"), 0, "", "", 0.1)

    class CorrectionGenerator:
        @staticmethod
        def _instruction(**_kwargs: Any) -> str:
            return "generate correction"

        def generate(self, _prompt: PromptRecord, paths, _resources: ResourceFiles):
            if failing_phase == "correction":
                raise error_type("process failed", process_metadata=metadata)
            paths.correction.write_text("test: {}\n", encoding="utf-8")
            from kathara_pipeline.models import CommandResult

            return CommandResult(("codex", "exec"), 0, "", "", 0.1)

    class Checker:
        def prepare_candidate(self, paths) -> dict[str, str]:
            paths.candidate.mkdir(parents=True)
            return {"lab.conf": "hash"}

        def build_command(self, **_kwargs: Any) -> list[str]:
            return ["checker"]

        def run(self, _paths, *, prepared: bool = False) -> CheckerRunResult:
            assert prepared
            raise error_type("process failed", process_metadata=metadata)

    class Validator:
        def __init__(self, _schema: Path, _skill: Path | None = None) -> None:
            pass

        def validate(self, _correction: Path, _lab: Path, _job: Path) -> ValidationResult:
            return ValidationResult(True, mode="documented-structural", data={"test": {}})

    pipeline.lab_generator = LabGenerator()  # type: ignore[assignment]
    pipeline.correction_generator = CorrectionGenerator()  # type: ignore[assignment]
    pipeline.checker_runner = Checker()  # type: ignore[assignment]
    monkeypatch.setattr("kathara_pipeline.pipeline.YamlValidator", Validator)

    outcome = pipeline.process_single_prompt(prompt, resources, force=False)

    assert outcome.status is JobStatus.ERROR
    manifest = json.loads(
        build_job_paths(config.paths.generated_labs, prompt.lab_id).manifest.read_text(encoding="utf-8")
    )
    assert manifest[manifest_field] == metadata
    assert manifest["phases"][-1]["name"] == "error"
    if failing_phase == "checker":
        report = json.loads(
            (
                build_job_paths(config.paths.generated_labs, prompt.lab_id).reports
                / "result-summary.json"
            ).read_text(encoding="utf-8")
        )
        assert report["status"] == "error"
        assert report["checker_execution_status"] == "timed_out"
        assert report["reports_missing"] == ["all", "failed", "summary"]
        assert manifest["test_result"]["reports_missing"] == (
            ["all", "failed", "summary"]
        )


def test_failed_job_never_stops_next_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path, continue_on_error=False)
    resources = _resources(tmp_path)
    prompts = [_prompt(tmp_path, "lab-1.md"), _prompt(tmp_path, "lab-2.md")]
    config.paths.generated_labs.mkdir()
    pipeline = Pipeline(config, emit=lambda _message: None)
    seen: list[str] = []
    monkeypatch.setattr(pipeline, "discover", lambda: prompts)
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    def process(prompt: PromptRecord, _resources: ResourceFiles, *, force: bool) -> JobSummary:
        seen.append(prompt.name)
        status = JobStatus.FAILED if len(seen) == 1 else JobStatus.PASSED
        return JobSummary(prompt.lab_id, prompt.name, status, lab_generated=True, lab_tested=True)

    monkeypatch.setattr(pipeline, "process_single_prompt", process)

    summary = pipeline.run()

    assert summary is not None
    assert seen == ["lab-1.md", "lab-2.md"]
    assert summary.counts == {"passed": 1, "failed": 1, "error": 0, "skipped": 0}
    assert (config.paths.generated_labs / "pipeline-summary.json").is_file()
    assert (config.paths.generated_labs / "pipeline-summary.csv").is_file()


@pytest.mark.parametrize(
    ("continue_on_error", "expected_seen"),
    [(True, ["lab-1.md", "lab-2.md"]), (False, ["lab-1.md"])],
)
def test_continue_on_error_controls_only_error_jobs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    continue_on_error: bool,
    expected_seen: list[str],
) -> None:
    config = _config(tmp_path, continue_on_error=continue_on_error)
    resources = _resources(tmp_path)
    prompts = [_prompt(tmp_path, "lab-1.md"), _prompt(tmp_path, "lab-2.md")]
    config.paths.generated_labs.mkdir()
    pipeline = Pipeline(config, emit=lambda _message: None)
    seen: list[str] = []
    monkeypatch.setattr(pipeline, "discover", lambda: prompts)
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    def process(prompt: PromptRecord, _resources: ResourceFiles, *, force: bool) -> JobSummary:
        seen.append(prompt.name)
        return JobSummary(prompt.lab_id, prompt.name, JobStatus.ERROR, error_message="technical")

    monkeypatch.setattr(pipeline, "process_single_prompt", process)

    summary = pipeline.run()

    assert summary is not None
    assert seen == expected_seen
    assert summary.counts["error"] == len(expected_seen)


def test_dry_run_has_no_filesystem_effects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    output: list[str] = []
    pipeline = Pipeline(config, emit=output.append)
    monkeypatch.setattr(pipeline, "discover", lambda: [prompt])
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    assert pipeline.run(dry_run=True) is None
    assert not config.paths.generated_labs.exists()
    assert any("checker argv:" in line for line in output)


def test_dry_run_warns_before_replacing_existing_job_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    paths = build_job_paths(config.paths.generated_labs, prompt.lab_id)
    ensure_generated_root_managed(config.paths.generated_labs, initialize=True)
    paths.root.mkdir(parents=True)
    output: list[str] = []
    pipeline = Pipeline(config, emit=output.append)
    monkeypatch.setattr(pipeline, "discover", lambda: [prompt])
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    assert pipeline.run(dry_run=True) is None

    assert any("verrebbe eliminata e ricreata" in line for line in output)


@pytest.mark.parametrize("prompt_kind", ["empty", "decode_error"])
def test_dry_run_warns_for_existing_job_even_when_prompt_cannot_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    prompt_kind: str,
) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    base = _prompt(tmp_path)
    prompt = PromptRecord(
        path=base.path,
        name=base.name,
        lab_id=base.lab_id,
        content="" if prompt_kind == "empty" else None,
        prompt_hash=base.prompt_hash,
        decode_error="UTF-8 non valido" if prompt_kind == "decode_error" else None,
    )
    paths = build_job_paths(config.paths.generated_labs, prompt.lab_id)
    ensure_generated_root_managed(config.paths.generated_labs, initialize=True)
    paths.root.mkdir(parents=True)
    (paths.root / "sentinel.txt").write_text("preserve in dry-run", encoding="utf-8")
    output: list[str] = []
    pipeline = Pipeline(config, emit=output.append)
    monkeypatch.setattr(pipeline, "discover", lambda: [prompt])
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    assert pipeline.run(dry_run=True) is None

    assert any("verrebbe eliminata e ricreata" in line for line in output)
    assert (paths.root / "sentinel.txt").read_text(encoding="utf-8") == "preserve in dry-run"


@pytest.mark.parametrize("job_path_kind", ["file", "symlink"])
def test_dry_run_reports_unsafe_existing_job_without_printing_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    job_path_kind: str,
) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    paths = build_job_paths(config.paths.generated_labs, prompt.lab_id)
    ensure_generated_root_managed(config.paths.generated_labs, initialize=True)
    if job_path_kind == "file":
        paths.root.write_text("not a job directory", encoding="utf-8")
    else:
        outside = tmp_path / "outside-job"
        outside.mkdir()
        paths.root.symlink_to(outside, target_is_directory=True)
    output: list[str] = []
    pipeline = Pipeline(config, emit=output.append)
    monkeypatch.setattr(pipeline, "discover", lambda: [prompt])
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    with pytest.raises(PreflightError, match="path job non sostituibile"):
        pipeline.run(dry_run=True)

    assert not any("Codex lab argv:" in line for line in output)
    assert paths.root.exists() or paths.root.is_symlink()


def test_completed_unchanged_job_is_skipped_unless_forced(tmp_path: Path) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    pipeline = Pipeline(config, emit=lambda _message: None)
    paths = build_job_paths(config.paths.generated_labs, prompt.lab_id)
    paths.correction_dir.mkdir(parents=True)
    paths.reports.mkdir()
    paths.correction.write_text("test: {}\n", encoding="utf-8")
    paths.candidate.mkdir(parents=True)
    raw = paths.reports / "checker" / "labs" / "candidate"
    raw.mkdir(parents=True)
    report_contents = {
        "labs/candidate/candidate_result_summary.csv": (
            "Total Tests,Passed Tests,Failed\n1,1,0\n"
        ),
        "labs/candidate/candidate_result_all.csv": (
            "Test Description,Passed,Reason\nexists,True,OK\n"
        ),
        "labs/candidate/candidate_result_failed.csv": (
            "Test Description,Passed,Reason\n"
        ),
    }
    report_names = list(report_contents)
    for relative, contents in report_contents.items():
        destination = paths.reports / "checker" / relative
        destination.write_text(contents, encoding="utf-8")
        (paths.checker_run / relative).write_text(contents, encoding="utf-8")
    write_json_atomic(
        paths.reports / "result-summary.json",
        {
            "status": "passed",
            "total_tests": 1,
            "passed_tests": 1,
            "failed_tests": 0,
            "checker_process_return_code": 0,
            "reports_found": report_names,
            "reports_missing": [],
        },
    )
    write_json_atomic(
        paths.manifest,
        {
            "status": "passed",
            "pipeline_version": __version__,
            "prompt_sha256": prompt.prompt_hash,
            "skill_sha256": resources.skill_hash,
            "schema_sha256": resources.schema_hash,
            "correction_sha256": sha256_file(paths.correction),
        },
    )

    assert pipeline._skip_reason(prompt, paths, resources, force=False) == "risultato completo e invariato"
    assert pipeline._skip_reason(prompt, paths, resources, force=True) is None

    (paths.reports / "checker" / report_names[-1]).unlink()
    assert pipeline._skip_reason(prompt, paths, resources, force=False) is None


def test_interrupted_job_is_not_skipped_and_is_recreated_from_scratch(tmp_path: Path) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    prompt = _prompt(tmp_path)
    pipeline = Pipeline(config, emit=lambda _message: None)
    paths = build_job_paths(config.paths.generated_labs, prompt.lab_id)
    ensure_generated_root_managed(config.paths.generated_labs, initialize=True)
    paths.root.mkdir(parents=True)
    stale = paths.root / "partial-output.txt"
    stale.write_text("incomplete", encoding="utf-8")
    write_json_atomic(
        paths.manifest,
        {
            "status": "discovered",
            "pipeline_version": __version__,
            "prompt_sha256": prompt.prompt_hash,
            "skill_sha256": resources.skill_hash,
            "schema_sha256": resources.schema_hash,
        },
    )

    assert pipeline._skip_reason(prompt, paths, resources, force=False) is None

    pipeline._prepare_new_job(paths)

    assert not stale.exists()
    assert paths.logs.is_dir()
    assert paths.reports.is_dir()
    assert paths.correction_dir.is_dir()


def test_job_setup_failure_becomes_terminal_error_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path)
    prompt = _prompt(tmp_path)
    pipeline = Pipeline(config, emit=lambda _message: None)
    monkeypatch.setattr(
        pipeline,
        "_prepare_new_job",
        lambda _paths: (_ for _ in ()).throw(OSError("disk unavailable")),
    )

    outcome = pipeline.process_single_prompt(prompt, _resources(tmp_path), force=False)

    assert outcome.status is JobStatus.ERROR
    assert "disk unavailable" in (outcome.error_message or "")


def test_empty_prompt_creates_skipped_manifest_with_explicit_reason(tmp_path: Path) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    path = tmp_path / "prompts_generates" / "empty.md"
    path.write_text("  \n", encoding="utf-8")
    prompt = PromptRecord(path, "empty.md", "empty", "  \n", sha256_text("  \n"))
    pipeline = Pipeline(config, emit=lambda _message: None)

    outcome = pipeline.process_single_prompt(prompt, resources, force=False)

    assert outcome.status is JobStatus.SKIPPED
    assert outcome.skip_reason == "prompt vuoto"
    manifest = json.loads(
        build_job_paths(config.paths.generated_labs, "empty").manifest.read_text(encoding="utf-8")
    )
    assert manifest["status"] == "skipped"
    assert manifest["skip_reason"] == "prompt vuoto"


def test_decode_error_continues_even_when_continue_on_error_is_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _config(tmp_path, continue_on_error=False)
    resources = _resources(tmp_path)
    broken_path = tmp_path / "prompts_generates" / "lab-1.md"
    broken = PromptRecord(
        broken_path,
        "lab-1.md",
        "lab-1",
        None,
        "raw-hash",
        "UTF-8 non valido",
    )
    good = _prompt(tmp_path, "lab-2.md")
    config.paths.generated_labs.mkdir()
    pipeline = Pipeline(config, emit=lambda _message: None)
    seen: list[str] = []
    monkeypatch.setattr(pipeline, "discover", lambda: [broken, good])
    monkeypatch.setattr(
        pipeline,
        "preflight",
        lambda _prompts, dry_run=False: PreflightReport(resources, (), ()),
    )

    def process(prompt: PromptRecord, _resources: ResourceFiles, *, force: bool) -> JobSummary:
        seen.append(prompt.name)
        status = JobStatus.ERROR if prompt.decode_error else JobStatus.PASSED
        return JobSummary(prompt.lab_id, prompt.name, status)

    monkeypatch.setattr(pipeline, "process_single_prompt", process)

    summary = pipeline.run()

    assert summary is not None
    assert seen == ["lab-1.md", "lab-2.md"]


def test_decode_error_job_persists_terminal_error_manifest(tmp_path: Path) -> None:
    config = _config(tmp_path)
    resources = _resources(tmp_path)
    path = tmp_path / "prompts_generates" / "broken.md"
    prompt = PromptRecord(
        path,
        "broken.md",
        "broken",
        None,
        "raw-hash",
        "Errore di decodifica UTF-8",
    )
    pipeline = Pipeline(config, emit=lambda _message: None)

    outcome = pipeline.process_single_prompt(prompt, resources, force=False)

    assert outcome.status is JobStatus.ERROR
    manifest = json.loads(
        build_job_paths(config.paths.generated_labs, "broken").manifest.read_text(encoding="utf-8")
    )
    assert manifest["status"] == "error"
    assert "decodifica" in manifest["errors"][0]
