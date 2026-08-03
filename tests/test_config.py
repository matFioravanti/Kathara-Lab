from __future__ import annotations

from pathlib import Path

import pytest

from kathara_pipeline.config import load_config
from kathara_pipeline.exceptions import ConfigurationError
from kathara_pipeline.paths import GENERATED_ROOT_MARKER, GENERATED_ROOT_MARKER_CONTENT


def test_load_config_resolves_defaults_from_config_parent(tmp_path: Path) -> None:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("{}\n", encoding="utf-8")

    config = load_config(config_path)

    assert config.paths.project_root == tmp_path.resolve()
    assert config.paths.prompts == (tmp_path / "prompts_generates").resolve()
    assert config.codex.timeout_seconds == 1800
    assert config.processing.continue_on_error is True


def test_load_config_rejects_unknown_keys(tmp_path: Path) -> None:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("processing:\n  max_attempts: 2\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="Chiavi sconosciute"):
        load_config(config_path)


def test_load_config_rejects_output_outside_project(tmp_path: Path) -> None:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("paths:\n  generated_labs: ../outside\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="dentro la root"):
        load_config(config_path)


def test_load_config_requires_csv_reports(tmp_path: Path) -> None:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("checker:\n  report_type: none\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="report_type"):
        load_config(config_path)


def test_load_config_requires_checker_no_cache(tmp_path: Path) -> None:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("checker:\n  no_cache: false\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="no_cache"):
        load_config(config_path)


def test_nested_config_resolves_paths_from_nearest_project_root(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    config_path = tmp_path / "configs" / "dev.yaml"
    config_path.parent.mkdir()
    config_path.write_text("{}\n", encoding="utf-8")

    config = load_config(config_path)

    assert config.paths.project_root == tmp_path.resolve()
    assert config.paths.prompts == (tmp_path / "prompts_generates").resolve()


@pytest.mark.parametrize(
    "generated_labs",
    ["prompts_generates", "prompts_generates/output", "kathara-lab-checker"],
)
def test_load_config_rejects_output_overlapping_inputs(
    tmp_path: Path, generated_labs: str
) -> None:
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        f"paths:\n  generated_labs: {generated_labs}\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="sovrapporsi"):
        load_config(config_path)


def test_load_config_rejects_populated_unowned_output_root(tmp_path: Path) -> None:
    output = tmp_path / "kathara-lab-generates"
    output.mkdir()
    (output / "important.txt").write_text("user data", encoding="utf-8")
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="non è gestita"):
        load_config(config_path)


def test_load_config_accepts_populated_owned_output_root(tmp_path: Path) -> None:
    output = tmp_path / "kathara-lab-generates"
    output.mkdir()
    (output / GENERATED_ROOT_MARKER).write_text(
        GENERATED_ROOT_MARKER_CONTENT, encoding="utf-8"
    )
    (output / "previous-job").mkdir()
    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text("{}\n", encoding="utf-8")

    assert load_config(config_path).paths.generated_labs == output.resolve()
