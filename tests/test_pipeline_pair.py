from __future__ import annotations

import csv
import shutil
from pathlib import Path

from kathara_pipeline.config import load_config
from kathara_pipeline.models import CommandResult, Variant
from kathara_pipeline.paths import build_experiment_paths, ensure_output_root
from kathara_pipeline.pipeline import Pipeline
from kathara_pipeline.prompt_discovery import discover_prompts
from kathara_pipeline.resource_discovery import discover_resources

_VALID_CORRECTION = (
    'lab_inline: |\n  r1[0]="A"\n  r2[0]="A"\n'
    'convergence_time: 10\n'
    'test:\n  requiring_startup: [r1, r2]\n'
    '  ip_mapping:\n    r1: {eth0: 10.0.0.1/24}\n    r2: {eth0: 10.0.0.2/24}\n'
    '  reachability:\n    r1: [10.0.0.2]\n    r2: [10.0.0.1]\n'
)

_INVALID_CORRECTION_NO_LAB_INLINE = (
    'convergence_time: 10\n'
    'test:\n  requiring_startup: [r1, r2]\n'
)

_VALID_LAB = (
    'r1[0]="A"\nr2[0]="A"\n',
    'ip addr replace 10.0.0.1/24 dev eth0\n',
    'ip addr replace 10.0.0.2/24 dev eth0\n',
)


def _make_project(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    project.mkdir()
    source_resources = Path(__file__).resolve().parents[1] / "resources"
    shutil.copytree(source_resources, project / "resources")
    (project / "pipeline.yaml").write_text(
        "paths:\n  resources: resources\n  output: results\n", encoding="utf-8"
    )
    prompts = tmp_path / "prompts"
    prompts.mkdir()
    (prompts / "one.md").write_text(
        "Create r1 and r2 on A, with r1 10.0.0.1/24 and r2 10.0.0.2/24.", encoding="utf-8"
    )
    return project, prompts


def _write_lab(workspace: Path) -> None:
    out = workspace / "output" / "lab"
    out.mkdir()
    (out / "lab.conf").write_text(_VALID_LAB[0], encoding="utf-8")
    (out / "r1.startup").write_text(_VALID_LAB[1], encoding="utf-8")
    (out / "r2.startup").write_text(_VALID_LAB[2], encoding="utf-8")


class FakeRunner:
    provider = "fake"
    model = "same-model"
    reasoning_effort = "same-effort"

    def __init__(self, correction_yaml: str = _VALID_CORRECTION):
        self.calls: list[tuple[str, Path]] = []
        self.correction_yaml = correction_yaml

    def build_command(self, *, instruction, workspace, output_last_message):
        return ("fake", instruction)

    def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
        self.calls.append((instruction, workspace))
        
        out = workspace / "output"
        out.mkdir(parents=True, exist_ok=True)
        
        if "EXACTLY THREE files" in instruction:
            (out / "evaluation-spec.md").write_text("Dummy evaluation spec", encoding="utf-8")
            (out / "check-plan.md").write_text("Dummy check plan", encoding="utf-8")
            (out / "evaluation-plan.yaml").write_text("checks:\n  - id: chk1\n    checker: reachability\n", encoding="utf-8")
        elif "binding an already-defined" in instruction or "failed validation" in instruction or "validated reference correction" in instruction:
            (out / "correction.yaml").write_text(self.correction_yaml, encoding="utf-8")
        else:
            _write_lab(workspace)
            
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", 1.0, False)


class FakeRunnerRetryFix(FakeRunner):
    def __init__(self):
        super().__init__()
        self._correction_attempts = 0

    def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
        self.calls.append((instruction, workspace))
        
        out = workspace / "output"
        out.mkdir(parents=True, exist_ok=True)
        
        if "EXACTLY THREE files" in instruction:
            (out / "evaluation-spec.md").write_text("Dummy evaluation spec", encoding="utf-8")
            (out / "check-plan.md").write_text("Dummy check plan", encoding="utf-8")
            (out / "evaluation-plan.yaml").write_text("checks:\n  - id: chk1\n    checker: reachability\n", encoding="utf-8")
        elif "binding an already-defined" in instruction or "failed validation" in instruction or "validated reference correction" in instruction:
            self._correction_attempts += 1
            content = _VALID_CORRECTION if self._correction_attempts > 1 else _INVALID_CORRECTION_NO_LAB_INLINE
            (out / "correction.yaml").write_text(content, encoding="utf-8")
        else:
            _write_lab(workspace)
            
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", 1.0, False)


class FakeChecker:
    def __init__(self, produce_reports: bool = True):
        self.order: list[str] = []
        self.corrections: list[Path] = []
        self.produce_reports = produce_reports

    def prepare_candidate(self, source, paths):
        if paths.checker_run.exists():
            shutil.rmtree(paths.checker_run)
        paths.labs_dir.mkdir(parents=True)
        shutil.copytree(source, paths.candidate)

    def run(self, *, correction, paths):
        paths.checker_run.mkdir(parents=True, exist_ok=True)
        self.order.append(paths.root.name)
        self.corrections.append(correction)
        if self.produce_reports:
            out = paths.checker_run / "results.csv"
            out.write_text("tests,passed,failed\n1,1,0\n", encoding="utf-8")
        return CommandResult(("fake-check",), 0, "", "", 1.0, False)

    def build_command(self, *, correction, paths):
        return ("checker", str(correction), str(paths.labs_dir))


def test_pipeline_runs_variants_in_new_order_and_shares_checker_skill(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.evaluation_plan_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)
    
    # Verify exact call order: 
    # 0: eval plan (spec + check plan)
    # 1: with_skill lab
    # 2: without_skill lab
    # 3: with_skill correction (full generation)
    # 4: without_skill correction (adaptation)
    assert len(fake_runner.calls) == 5
    assert "evaluation-spec.md" in fake_runner.calls[0][0] and "check-plan.md" in fake_runner.calls[0][0]
    
    assert "resources/creation/SKILL.md" in fake_runner.calls[1][0] # with_skill lab
    assert "Read only input/prompt.md" in fake_runner.calls[2][0] # without_skill lab
    
    with_corr_call = fake_runner.calls[3][0]
    without_corr_call = fake_runner.calls[4][0]
    
    assert "binding an already-defined" in with_corr_call
    assert "resources/checker/SKILL.md" in with_corr_call
    
    assert "validated reference correction" in without_corr_call
    assert "output/correction.yaml" in without_corr_call
    
    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2
    exp = summary.experiments[0]
    assert exp.evaluation_spec_generated
    assert exp.check_plan_generated
    assert exp.with_skill.correction_generated
    assert exp.without_skill.correction_generated
    assert exp.with_skill.correction_mode == "full_generation"
    assert exp.without_skill.correction_mode == "adaptation"
    assert exp.with_skill.status.value == "passed"
    assert exp.without_skill.status.value == "passed"
    assert exp.comparison.value == "EQUAL"


def test_checker_is_not_called_when_correction_is_invalid(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner(correction_yaml=_INVALID_CORRECTION_NO_LAB_INLINE)
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.evaluation_plan_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)
    
    assert fake_checker.corrections == []
    assert fake_checker.order == []
    exp = summary.experiments[0]
    assert not exp.with_skill.correction_generated
    assert not exp.without_skill.correction_generated
    assert exp.with_skill.status.value == "error"
    assert exp.without_skill.status.value == "error"


def test_retry_fixes_correction_missing_lab_inline(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunnerRetryFix()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.evaluation_plan_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)
    
    correction_calls = [c for c, _ in fake_runner.calls if "binding an already-defined" in c or "regenerate" in c or "validated reference correction" in c or "in place" in c]
    # Expect: 1. with_skill corr (fails), 2. with_skill corr retry (passes), 3. without_skill corr (fails, it's fake runner), 4. without_skill corr retry (passes)
    # Actually FakeRunnerRetryFix increments total correction_attempts across both variants.
    # So attempt 1 fails, attempt 2 (retry with_skill) passes.
    # Then without_skill gets attempt 3, which passes immediately!
    assert len(correction_calls) == 3
    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2
    exp = summary.experiments[0]
    assert exp.with_skill.correction_generated
    assert exp.without_skill.correction_generated


def test_checker_cleanup_on_technical_failure(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.evaluation_plan_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner

    class FakeFailingChecker(FakeChecker):
        def run(self, *, correction, paths):
            super().run(correction=correction, paths=paths)
            return CommandResult(("fake-check",), 1, "", "", 1.0, False)

    fake_checker = FakeFailingChecker(produce_reports=False)
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)

    exp = summary.experiments[0]
    assert exp.with_skill.status.value == "error"
    assert "technical return code" in exp.with_skill.error_message

    with_skill_paths = build_experiment_paths(project / "results", exp.experiment_id).with_skill
    assert not with_skill_paths.checker_run.exists()


class FakeRunnerEvalSpecFails(FakeRunner):
    def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
        self.calls.append((instruction, workspace))
        if "EXACTLY TWO files" in instruction:
            stdout_log.parent.mkdir(parents=True, exist_ok=True)
            stdout_log.write_text("{}\n", encoding="utf-8")
            stderr_log.write_text("Error", encoding="utf-8")
            return CommandResult(("fake",), 1, "", "Error", 1.0, False)
        out = workspace / "output"
        out.mkdir(parents=True, exist_ok=True)
        if "per-variant" in instruction or "failed validation" in instruction or "copy" in instruction:
            (out / "correction.yaml").write_text(self.correction_yaml, encoding="utf-8")
        else:
            _write_lab(workspace)
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", 1.0, False)


def test_checker_is_not_called_when_eval_spec_fails(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunnerEvalSpecFails()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.evaluation_plan_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)
    
    assert fake_checker.corrections == []
    exp = summary.experiments[0]
    assert not exp.evaluation_spec_generated
    assert not exp.check_plan_generated
    assert not exp.with_skill.correction_generated
    assert not exp.without_skill.correction_generated
    assert exp.with_skill.status.value == "error"
    assert "Generazione correction fallita o saltata" in exp.with_skill.error_message


def test_resume_from_correction(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.evaluation_plan_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    
    summary = pipeline.run(discover_prompts(prompts), resources)
    assert summary.experiments[0].with_skill.status.value == "passed"
    
    fake_runner.calls.clear()
    fake_checker.corrections.clear()
    fake_checker.order.clear()
    
    config_resume = config.with_overrides(resume_from="correction")
    pipeline_resume = Pipeline(config_resume)
    pipeline_resume.runner = fake_runner
    pipeline_resume.lab_generator.runner = fake_runner
    pipeline_resume.evaluation_plan_generator.runner = fake_runner
    pipeline_resume.correction_generator.runner = fake_runner
    pipeline_resume.checker = fake_checker
    
    summary2 = pipeline_resume.run(discover_prompts(prompts), resources)
    
    # Should only run correction for with_skill and without_skill
    assert len(fake_runner.calls) == 2
    assert "binding an already-defined" in fake_runner.calls[0][0]
    assert "validated reference correction" in fake_runner.calls[1][0]
    
    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2
    
    assert summary2.experiments[0].with_skill.status.value == "passed"
    assert summary2.experiments[0].without_skill.status.value == "passed"
