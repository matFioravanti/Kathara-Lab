from pathlib import Path

from kathara_pipeline.lab_generator import LabGenerator
from kathara_pipeline.models import ResourceFiles, Variant
from kathara_pipeline.paths import build_experiment_paths


class DummyRunner:
    provider = "dummy"
    model = None
    reasoning_effort = None


def test_creation_skill_exists_only_in_with_skill_workspace(tmp_path: Path):
    creation = tmp_path / "creation.md"; creation.write_text("skill", encoding="utf-8")
    checker = tmp_path / "checker.md"; checker.write_text("checker", encoding="utf-8")
    schema = tmp_path / "schema.md"; schema.write_text("schema", encoding="utf-8")
    resources = ResourceFiles(tmp_path, creation, checker, schema, "a", "b", "c")
    paths = build_experiment_paths(tmp_path / "out", "exp")
    generator = LabGenerator(DummyRunner(), 10)
    generator.prepare_workspace(paths=paths.with_skill, prompt_text="p", variant=Variant.WITH_SKILL, resources=resources)
    generator.prepare_workspace(paths=paths.without_skill, prompt_text="p", variant=Variant.WITHOUT_SKILL, resources=resources)
    assert (paths.with_skill.workspace / "resources" / "creation" / "SKILL.md").is_file()
    assert not (paths.without_skill.workspace / "resources").exists()
