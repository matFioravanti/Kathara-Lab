from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from kathara_pipeline.config import load_config
from kathara_pipeline.exceptions import PreflightError
from kathara_pipeline.models import PromptRecord
from kathara_pipeline.preflight import run_preflight
from kathara_pipeline.paths import GENERATED_ROOT_MARKER, GENERATED_ROOT_MARKER_CONTENT
from kathara_pipeline.prompt_discovery import discover_prompts


def _project(tmp_path: Path) -> Path:
    (tmp_path / "prompts_generates").mkdir()
    checker = tmp_path / "kathara-lab-checker"
    (checker / "references").mkdir(parents=True)
    (checker / "SKILL.md").write_text(
        "YAML correction.yaml with lab_inline; see references/config-schema.md",
        encoding="utf-8",
    )
    (checker / "references" / "config-schema.md").write_text(
        "# schema\n```yaml\nlab_inline: |\n  r1[0]=\"lan\"\ntest:\n  requiring_startup: []\n```\n",
        encoding="utf-8",
    )
    (tmp_path / "pipeline.yaml").write_text("{}\n", encoding="utf-8")
    return tmp_path / "pipeline.yaml"


def test_dry_preflight_does_not_create_generated_root(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = _project(tmp_path)
    config = load_config(config_path)
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, discover_prompts(config.paths.prompts), dry_run=True)

    assert report.ok
    assert report.warnings
    assert not config.paths.generated_labs.exists()


def test_preflight_detects_unsafe_generated_root(tmp_path: Path, monkeypatch) -> None:
    config_path = _project(tmp_path)
    config = load_config(config_path)
    unsafe_paths = replace(config.paths, generated_labs=config.paths.project_root)
    config = replace(config, paths=unsafe_paths)
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, [], dry_run=True)

    assert not report.ok
    assert any("Root di output non sicura" in error for error in report.errors)


def test_preflight_blocks_unreadable_prompt_record(tmp_path: Path, monkeypatch) -> None:
    config_path = _project(tmp_path)
    config = load_config(config_path)
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)
    prompt = PromptRecord(
        path=config.paths.prompts / "broken.md",
        name="broken.md",
        lab_id="broken",
        content=None,
        prompt_hash=None,
        decode_error="Errore di lettura",
    )

    report = run_preflight(config, [prompt], dry_run=True)

    assert not report.ok
    assert any("File prompt non leggibili" in error for error in report.errors)


def test_preflight_blocks_lab_ids_that_differ_only_by_case(
    tmp_path: Path, monkeypatch
) -> None:
    config = load_config(_project(tmp_path))
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)
    prompts = [
        PromptRecord(
            path=config.paths.prompts / "Foo!.md",
            name="Foo!.md",
            lab_id="Foo",
            content="first",
            prompt_hash="first",
        ),
        PromptRecord(
            path=config.paths.prompts / "foo?.txt",
            name="foo?.txt",
            lab_id="foo",
            content="second",
            prompt_hash="second",
        ),
    ]

    report = run_preflight(config, prompts, dry_run=True)

    assert not report.ok
    assert any("Foo / foo" in error for error in report.errors)


def test_dry_preflight_accepts_nested_output_with_missing_intermediate_directories(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = _project(tmp_path)
    config_path.write_text("paths:\n  generated_labs: build/generated/labs\n", encoding="utf-8")
    config = load_config(config_path)
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, [], dry_run=True)

    assert report.ok
    assert not (tmp_path / "build").exists()


def test_preflight_defensively_rejects_output_overlap(tmp_path: Path, monkeypatch) -> None:
    config = load_config(_project(tmp_path))
    unsafe_paths = replace(config.paths, generated_labs=config.paths.checker_resources)
    config = replace(config, paths=unsafe_paths)
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, [], dry_run=True)

    assert not report.ok
    assert any("sovrappone" in error for error in report.errors)


def test_resource_read_failure_is_a_preflight_error(
    tmp_path: Path, monkeypatch
) -> None:
    config = load_config(_project(tmp_path))
    monkeypatch.setattr(
        "kathara_pipeline.preflight.discover_resources",
        lambda _root: (_ for _ in ()).throw(OSError("permission denied")),
    )

    with pytest.raises(PreflightError, match="risorse locali"):
        run_preflight(config, [], dry_run=True)


def test_preflight_blocks_new_markdown_fields_without_semantic_support(
    tmp_path: Path, monkeypatch
) -> None:
    config = load_config(_project(tmp_path))
    schema = config.paths.checker_resources / "references" / "config-schema.md"
    schema.write_text(
        "# future\n```yaml\nlab_inline: x\ntest:\n  future_check: {}\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, [], dry_run=True)

    assert not report.ok
    assert any("$.test.future_check" in error for error in report.errors)


def test_dry_preflight_rejects_unowned_existing_output_root(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = _project(tmp_path)
    config = load_config(config_path)
    output = tmp_path / "kathara-lab-generates"
    output.mkdir()
    (output / "not-owned").write_text("data", encoding="utf-8")
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, [], dry_run=True)

    assert not report.ok
    assert any("non è gestita" in error for error in report.errors)


def test_normal_preflight_initializes_output_marker(tmp_path: Path, monkeypatch) -> None:
    config = load_config(_project(tmp_path))
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    run_preflight(config, [], dry_run=False)

    marker = config.paths.generated_labs / GENERATED_ROOT_MARKER
    assert marker.read_text(encoding="utf-8") == GENERATED_ROOT_MARKER_CONTENT


def test_preflight_rejects_intermediate_output_symlink_added_after_config_load(
    tmp_path: Path, monkeypatch
) -> None:
    config_path = _project(tmp_path)
    config_path.write_text(
        "paths:\n  generated_labs: build/generated\n",
        encoding="utf-8",
    )
    config = load_config(config_path)
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    (tmp_path / "build").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr("kathara_pipeline.preflight.shutil.which", lambda _name: None)

    report = run_preflight(config, [], dry_run=False)

    assert not report.ok
    assert any("deve restare nel progetto" in error for error in report.errors)
    assert not (outside / "generated").exists()
