from __future__ import annotations

from pathlib import Path

import pytest

from kathara_pipeline.exceptions import PreflightError
from kathara_pipeline.resource_discovery import discover_resources


def test_discovers_markdown_schema_explicitly_referenced_by_skill(tmp_path: Path) -> None:
    resources = tmp_path / "checker"
    references = resources / "references"
    references.mkdir(parents=True)
    (resources / "SKILL.md").write_text(
        "Read references/config-schema.md for the schema.", encoding="utf-8"
    )
    schema = references / "config-schema.md"
    schema.write_text("# Schema\n`lab_inline`\n", encoding="utf-8")

    found = discover_resources(resources)

    assert found.skill_path == (resources / "SKILL.md").resolve()
    assert found.schema_path == schema.resolve()
    assert found.schema_mode == "documented-structure"


def test_recognizes_json_schema(tmp_path: Path) -> None:
    resources = tmp_path / "checker"
    resources.mkdir()
    (resources / "SKILL.md").write_text("skill", encoding="utf-8")
    schema = resources / "config-schema.json"
    schema.write_text(
        '{"$schema":"https://json-schema.org/draft/2020-12/schema",'
        '"type":"object","properties":{}}',
        encoding="utf-8",
    )

    assert discover_resources(resources).schema_mode == "json-schema"


def test_rejects_external_skill_symlink(tmp_path: Path) -> None:
    resources = tmp_path / "checker"
    resources.mkdir()
    external = tmp_path / "external-skill.md"
    external.write_text("secret skill", encoding="utf-8")
    try:
        (resources / "SKILL.md").symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")

    with pytest.raises(PreflightError, match="symlink"):
        discover_resources(resources)


def test_rejects_external_schema_symlink(tmp_path: Path) -> None:
    resources = tmp_path / "checker"
    resources.mkdir()
    (resources / "SKILL.md").write_text("Read config-schema.md", encoding="utf-8")
    external = tmp_path / "external-schema.md"
    external.write_text("secret schema", encoding="utf-8")
    try:
        (resources / "config-schema.md").symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")

    with pytest.raises(PreflightError, match="symlink"):
        discover_resources(resources)


def test_rejects_external_examples_symlink(tmp_path: Path) -> None:
    resources = tmp_path / "checker"
    resources.mkdir()
    (resources / "SKILL.md").write_text("Read config-schema.md", encoding="utf-8")
    (resources / "config-schema.md").write_text("schema", encoding="utf-8")
    external = tmp_path / "external-examples"
    external.mkdir()
    try:
        (resources / "examples").symlink_to(external, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")

    with pytest.raises(PreflightError, match="examples.*symlink"):
        discover_resources(resources)
