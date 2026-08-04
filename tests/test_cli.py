from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from kathara_pipeline import cli
from kathara_pipeline.exceptions import ConfigurationError, PreflightError
from kathara_pipeline.models import (
    JobStatus,
    PipelineSummary,
    PromptRecord,
    ValidationResult,
)
from kathara_pipeline.paths import ensure_generated_root_managed
from kathara_pipeline.state_store import write_json_atomic


def _config(generated_root: Path) -> SimpleNamespace:
    return SimpleNamespace(paths=SimpleNamespace(generated_labs=generated_root))


def _summary(*, failed: int = 0, error: int = 0) -> PipelineSummary:
    return PipelineSummary(
        pipeline_version="0.1.0",
        started_at="2026-08-03T00:00:00Z",
        finished_at="2026-08-03T00:00:01Z",
        duration_seconds=1.0,
        prompts_found=1,
        labs_generated=1,
        checker_attempted=1,
        checker_completed=1,
        counts={"passed": int(not failed and not error), "failed": failed, "error": error, "skipped": 0},
    )


def _mock_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[Mock, Mock, SimpleNamespace]:
    config = _config(tmp_path / "generated")
    pipeline = Mock()
    pipeline_type = Mock(return_value=pipeline)
    monkeypatch.setattr(cli, "load_config", Mock(return_value=config))
    monkeypatch.setattr(cli, "Pipeline", pipeline_type)
    return pipeline, pipeline_type, config


def test_parser_requires_exactly_one_run_selection() -> None:
    parser = cli.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["run"])
    with pytest.raises(SystemExit):
        parser.parse_args(["run", "--all", "--prompt", "lab.md"])


def test_config_option_is_accepted_before_or_after_command() -> None:
    parser = cli.build_parser()

    before = parser.parse_args(["--config", "before.yaml", "status"])
    after = parser.parse_args(["status", "--config", "after.yaml"])

    assert before.config == Path("before.yaml")
    assert after.config == Path("after.yaml")


def test_run_all_delegates_to_pipeline_and_returns_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline, pipeline_type, config = _mock_pipeline(monkeypatch, tmp_path)
    pipeline.run.return_value = _summary()

    exit_code = cli.main(["--config", "custom.yaml", "run", "--all"])

    assert exit_code == cli.EXIT_SUCCESS
    cli.load_config.assert_called_once_with(Path("custom.yaml"))
    pipeline_type.assert_called_once_with(config)
    pipeline.run.assert_called_once_with(prompt_name=None, force=False, dry_run=False)


def test_run_prompt_forwards_force_and_dry_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline, _, _ = _mock_pipeline(monkeypatch, tmp_path)
    pipeline.run.return_value = None

    exit_code = cli.main(
        ["run", "--prompt", "lab-001.md", "--force", "--dry-run", "--config", "custom.yaml"]
    )

    assert exit_code == cli.EXIT_SUCCESS
    pipeline.run.assert_called_once_with(
        prompt_name="lab-001.md",
        force=True,
        dry_run=True,
    )


@pytest.mark.parametrize(
    ("summary", "expected"),
    [
        (_summary(), cli.EXIT_SUCCESS),
        (_summary(failed=1), cli.EXIT_FAILED),
        (_summary(error=1), cli.EXIT_ERROR),
        (_summary(failed=1, error=1), cli.EXIT_ERROR),
    ],
)
def test_run_uses_documented_worst_status_exit_code(
    summary: PipelineSummary,
    expected: int,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pipeline, _, _ = _mock_pipeline(monkeypatch, tmp_path)
    pipeline.run.return_value = summary

    assert cli.main(["run", "--all"]) == expected


def test_preflight_discovers_then_runs_real_preflight_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline, _, _ = _mock_pipeline(monkeypatch, tmp_path)
    prompts = [
        PromptRecord(Path("lab.md"), "lab.md", "lab", "prompt", "hash")
    ]
    pipeline.discover.return_value = prompts

    assert cli.main(["preflight"]) == cli.EXIT_SUCCESS

    pipeline.preflight.assert_called_once_with(prompts, dry_run=False)
    assert "Preflight completato con successo" in capsys.readouterr().out


def test_config_or_preflight_failure_returns_exit_three(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        cli,
        "load_config",
        Mock(side_effect=ConfigurationError("config non valida")),
    )

    assert cli.main(["run", "--all"]) == cli.EXIT_PREFLIGHT
    assert "config non valida" in capsys.readouterr().err

    pipeline, _, _ = _mock_pipeline(monkeypatch, tmp_path)
    pipeline.discover.return_value = []
    pipeline.preflight.side_effect = PreflightError("preflight fallito", ["Docker non attivo"])

    assert cli.main(["preflight"]) == cli.EXIT_PREFLIGHT
    error_output = capsys.readouterr().err
    assert "preflight fallito" in error_output
    assert "Docker non attivo" in error_output


def _write_config(project: Path) -> Path:
    config_path = project / "pipeline.yaml"
    config_path.write_text("{}\n", encoding="utf-8")
    return config_path


def test_status_reads_summary_and_manifests_without_constructing_pipeline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = _write_config(tmp_path)
    generated = tmp_path / "kathara-lab-generates"
    ensure_generated_root_managed(generated, initialize=True)
    write_json_atomic(
        generated / "pipeline-summary.json",
        {
            "prompts_found": 2,
            "labs_generated": 2,
            "labs_tested": 1,
            "counts": {"passed": 1, "failed": 0, "error": 1, "skipped": 0},
        },
    )
    write_json_atomic(
        generated / "lab-002" / "manifest.json",
        {"lab_id": "lab-002", "status": JobStatus.ERROR},
    )
    write_json_atomic(
        generated / "lab-001" / "manifest.json",
        {"lab_id": "lab-001", "status": JobStatus.PASSED},
    )
    monkeypatch.setattr(cli, "Pipeline", Mock(side_effect=AssertionError("Pipeline non prevista")))

    assert cli.main(["status", "--config", str(config_path)]) == cli.EXIT_ERROR

    output = capsys.readouterr().out
    assert "Prompt trovati: 2" in output
    assert output.index("lab-001: passed") < output.index("lab-002: error")


def test_status_returns_failed_exit_code_for_persisted_failed_job(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = _write_config(tmp_path)
    ensure_generated_root_managed(tmp_path / "kathara-lab-generates", initialize=True)
    write_json_atomic(
        tmp_path / "kathara-lab-generates" / "lab-001" / "manifest.json",
        {"lab_id": "lab-001", "status": JobStatus.FAILED},
    )

    assert cli.main(["status", "--config", str(config_path)]) == cli.EXIT_FAILED
    assert "lab-001: failed" in capsys.readouterr().out


def test_status_with_no_persisted_state_is_successful_and_read_only(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = _write_config(tmp_path)
    generated = tmp_path / "kathara-lab-generates"

    assert cli.main(["--config", str(config_path), "status"]) == cli.EXIT_SUCCESS

    assert "Nessuna esecuzione registrata" in capsys.readouterr().out
    assert not generated.exists()


def test_validate_uses_dry_preflight_and_static_validators_only(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline, _, config = _mock_pipeline(monkeypatch, tmp_path)
    job = config.paths.generated_labs / "lab-001"
    source = job / "source"
    source.mkdir(parents=True)
    (job / "prompt.md").write_text("prompt", encoding="utf-8")
    correction = job / "correction" / "correction.yaml"
    correction.parent.mkdir()
    correction.write_text("test: {}\n", encoding="utf-8")
    prompt = PromptRecord(Path("lab-001.md"), "lab-001.md", "lab-001", "prompt", "hash")
    pipeline.discover.return_value = [prompt]
    schema = tmp_path / "config-schema.md"
    skill = tmp_path / "SKILL.md"
    pipeline.preflight.return_value = SimpleNamespace(
        resources=SimpleNamespace(schema_path=schema, skill_path=skill)
    )

    lab_validator = Mock()
    lab_validator.validate.return_value = ValidationResult(True, mode="static")
    yaml_validator = Mock()
    yaml_validator.validate.return_value = ValidationResult(True, mode="documented-structural")
    lab_validator_type = Mock(return_value=lab_validator)
    yaml_validator_type = Mock(return_value=yaml_validator)
    monkeypatch.setattr(cli, "LabValidator", lab_validator_type)
    monkeypatch.setattr(cli, "YamlValidator", yaml_validator_type)

    assert cli.main(["validate"]) == cli.EXIT_SUCCESS

    pipeline.preflight.assert_called_once_with([prompt], dry_run=True)
    lab_validator.validate.assert_called_once_with(source, "prompt")
    yaml_validator_type.assert_called_once_with(schema, skill)
    yaml_validator.validate.assert_called_once_with(correction, source, job)
    assert "2 artefatti validi" in capsys.readouterr().out


def test_validate_returns_two_for_invalid_existing_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline, _, config = _mock_pipeline(monkeypatch, tmp_path)
    source = config.paths.generated_labs / "lab-001" / "source"
    source.mkdir(parents=True)
    pipeline.discover.return_value = []
    pipeline.preflight.return_value = SimpleNamespace(
        resources=SimpleNamespace(schema_path=tmp_path / "schema.md")
    )
    lab_validator = Mock()
    lab_validator.validate.return_value = ValidationResult(False, ("lab.conf mancante",))
    monkeypatch.setattr(cli, "LabValidator", Mock(return_value=lab_validator))
    monkeypatch.setattr(cli, "YamlValidator", Mock(return_value=Mock()))

    assert cli.main(["validate"]) == cli.EXIT_ERROR
    assert "lab.conf mancante" in capsys.readouterr().out


def test_validate_with_no_artifacts_does_not_create_generated_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    pipeline, _, config = _mock_pipeline(monkeypatch, tmp_path)
    pipeline.discover.return_value = []
    pipeline.preflight.return_value = SimpleNamespace(
        resources=SimpleNamespace(schema_path=tmp_path / "schema.md")
    )

    assert cli.main(["validate"]) == cli.EXIT_SUCCESS

    assert not config.paths.generated_labs.exists()
    assert "nessun artefatto" in capsys.readouterr().out
