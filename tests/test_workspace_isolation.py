from pathlib import Path

from kathara_pipeline.evaluation_plan_generator import EvaluationPlanGenerator
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

def test_evaluation_plan_workspace_isolation(tmp_path: Path):
    creation = tmp_path / "creation.md"; creation.write_text("skill", encoding="utf-8")
    checker = tmp_path / "checker.md"; checker.write_text("checker", encoding="utf-8")
    schema = tmp_path / "schema.md"; schema.write_text("schema", encoding="utf-8")
    resources = ResourceFiles(tmp_path, creation, checker, schema, "a", "b", "c")
    paths = build_experiment_paths(tmp_path / "out", "exp")
    
    # ensure candidates are created (simulate pipeline)
    paths.with_skill.workspace.mkdir(parents=True)
    paths.without_skill.workspace.mkdir(parents=True)
    (paths.with_skill.workspace / "candidate.txt").write_text("with", encoding="utf-8")
    (paths.without_skill.workspace / "candidate.txt").write_text("without", encoding="utf-8")

    generator = EvaluationPlanGenerator(DummyRunner(), 10)
    generator.prepare_workspace(paths=paths, prompt_text="p", resources=resources)

    # Check that evaluation_plan_workspace has only input and output and resources
    workspace = paths.evaluation_plan_workspace
    assert (workspace / "input" / "prompt.md").is_file()
    assert (workspace / "resources" / "creation" / "SKILL.md").is_file()
    assert (workspace / "resources" / "checker" / "SKILL.md").is_file()
    assert (workspace / "resources" / "checker" / "config-schema.md").is_file()
    assert (workspace / "output").is_dir()
    
    # Must NOT have candidates or other things
    assert not (workspace / "with_skill").exists()
    assert not (workspace / "without_skill").exists()
    
    # Check that only these 3 things exist in workspace
    entries = {e.name for e in workspace.iterdir()}
    assert entries == {"input", "resources", "output"}

def test_correction_workspace_isolation(tmp_path: Path):
    from kathara_pipeline.correction_generator import CorrectionGenerator
    creation = tmp_path / "creation.md"; creation.write_text("skill", encoding="utf-8")
    checker = tmp_path / "checker.md"; checker.write_text("checker", encoding="utf-8")
    schema = tmp_path / "schema.md"; schema.write_text("schema", encoding="utf-8")
    resources = ResourceFiles(tmp_path, creation, checker, schema, "a", "b", "c")
    paths = build_experiment_paths(tmp_path / "out", "exp")
    
    paths.evaluation_spec.parent.mkdir(parents=True, exist_ok=True)
    paths.evaluation_spec.write_text("eval spec", encoding="utf-8")
    paths.check_plan.write_text("check plan", encoding="utf-8")
    
    paths.with_skill.source.mkdir(parents=True)
    (paths.with_skill.source / "lab.conf").write_text("lab", encoding="utf-8")

    generator = CorrectionGenerator(DummyRunner(), 10)
    generator.prepare_workspace(experiment_paths=paths, variant_paths=paths.with_skill, prompt_text="p", resources=resources)

    workspace = paths.with_skill.correction_workspace
    assert (workspace / "input" / "prompt.md").is_file()
    assert (workspace / "input" / "evaluation-spec.md").is_file()
    assert (workspace / "input" / "check-plan.md").is_file()
    assert (workspace / "resources" / "checker" / "SKILL.md").is_file()
    assert (workspace / "candidate" / "lab.conf").is_file()
    assert (workspace / "output").is_dir()
    
    entries = {e.name for e in workspace.iterdir()}
    assert entries == {"input", "resources", "candidate", "output"}
