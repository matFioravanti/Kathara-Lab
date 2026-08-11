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


def test_correction_workspace_isolation(tmp_path: Path):
    from kathara_pipeline.correction_generator import CorrectionGenerator
    creation = tmp_path / "creation.md"; creation.write_text("skill", encoding="utf-8")
    checker = tmp_path / "checker.md"; checker.write_text("checker", encoding="utf-8")
    schema = tmp_path / "schema.md"; schema.write_text("schema", encoding="utf-8")
    resources = ResourceFiles(tmp_path, creation, checker, schema, "a", "b", "c")
    paths = build_experiment_paths(tmp_path / "out", "exp")

    paths.with_skill.source.mkdir(parents=True)
    (paths.with_skill.source / "lab.conf").write_text("lab", encoding="utf-8")

    generator = CorrectionGenerator(DummyRunner(), 10)
    generator.prepare_workspace(experiment_paths=paths, variant_paths=paths.with_skill, prompt_text="my prompt", resources=resources)

    workspace = paths.with_skill.correction_workspace
    # Prompt is now written to workspace instead of evaluation-plan.yaml
    assert (workspace / "input" / "prompt.md").is_file()
    assert (workspace / "input" / "prompt.md").read_text() == "my prompt"
    assert not (workspace / "input" / "evaluation-plan.yaml").exists()
    assert not (workspace / "input" / "evaluation-spec.md").exists()
    assert not (workspace / "input" / "check-plan.md").exists()
    assert (workspace / "resources" / "checker" / "SKILL.md").is_file()
    assert (workspace / "candidate" / "lab.conf").is_file()
    assert (workspace / "output").is_dir()

    entries = {e.name for e in workspace.iterdir()}
    assert entries == {"input", "resources", "candidate", "output"}
