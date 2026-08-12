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


def _is_paired_correction_call(instruction: str) -> bool:
    """Detect a paired correction call by checking for paired workspace markers."""
    return "candidates/with_skill" in instruction or "output/with_skill/correction.yaml" in instruction


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

        if _is_paired_correction_call(instruction):
            # Paired generation: write both corrections
            (out / "with_skill").mkdir(parents=True, exist_ok=True)
            (out / "without_skill").mkdir(parents=True, exist_ok=True)
            (out / "with_skill" / "correction.yaml").write_text(self.correction_yaml, encoding="utf-8")
            (out / "without_skill" / "correction.yaml").write_text(self.correction_yaml, encoding="utf-8")
        elif "Read input/prompt.md to understand what must be tested" in instruction or "execution failed" in instruction:
            # Standalone correction (or retry)
            (out / "correction.yaml").write_text(self.correction_yaml, encoding="utf-8")
        else:
            _write_lab(workspace)

        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", 1.0, False)


class FakeRunnerRetryFix(FakeRunner):
    """Standalone runner that fails the first correction attempt then succeeds."""

    def __init__(self):
        super().__init__()
        self._correction_attempts = 0

    def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
        self.calls.append((instruction, workspace))

        out = workspace / "output"
        out.mkdir(parents=True, exist_ok=True)

        is_correction = (
            _is_paired_correction_call(instruction)
            or "Read input/prompt.md to understand what must be tested" in instruction
            or "execution failed" in instruction
        )

        if is_correction:
            self._correction_attempts += 1
            content = _VALID_CORRECTION if self._correction_attempts > 1 else _INVALID_CORRECTION_NO_LAB_INLINE
            if _is_paired_correction_call(instruction):
                (out / "with_skill").mkdir(parents=True, exist_ok=True)
                (out / "without_skill").mkdir(parents=True, exist_ok=True)
                (out / "with_skill" / "correction.yaml").write_text(content, encoding="utf-8")
                (out / "without_skill" / "correction.yaml").write_text(content, encoding="utf-8")
            else:
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


# ------------------------------------------------------------------ #
# Tests                                                               #
# ------------------------------------------------------------------ #

def test_pipeline_runs_variants_and_shares_checker_skill(tmp_path: Path):
    """Both labs valid → 3 runner calls (2 lab + 1 paired correction)."""
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)

    # 2 lab calls + 1 paired correction call = 3 total
    assert len(fake_runner.calls) == 3, (
        f"Expected 3 runner calls (2 lab + 1 paired correction), got {len(fake_runner.calls)}"
    )

    # The third call is the paired correction
    paired_call_instruction = fake_runner.calls[2][0]
    assert _is_paired_correction_call(paired_call_instruction), \
        "Third call should be a paired correction call"



    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2

    exp = summary.experiments[0]
    assert exp.with_skill.correction_generated
    assert exp.without_skill.correction_generated
    assert exp.with_skill.correction_mode == "paired_generation"
    assert exp.without_skill.correction_mode == "paired_generation"
    assert exp.with_skill.status.value == "passed"
    assert exp.without_skill.status.value == "passed"
    assert exp.comparison.value == "EQUAL"



def test_checker_cleanup_on_technical_failure(tmp_path: Path):
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
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


def test_resume_from_correction(tmp_path: Path):
    """Resume from correction: 1 paired call (not 2 separate calls)."""
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
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
    pipeline_resume.correction_generator.runner = fake_runner
    pipeline_resume.checker = fake_checker

    summary2 = pipeline_resume.run(discover_prompts(prompts), resources)

    # Paired: 1 correction call for both variants (not 2 separate)
    assert len(fake_runner.calls) == 1, (
        f"Expected 1 paired correction call on resume, got {len(fake_runner.calls)}"
    )
    assert _is_paired_correction_call(fake_runner.calls[0][0]), \
        "Resume correction call should be paired"

    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2

    assert summary2.experiments[0].with_skill.status.value == "passed"
    assert summary2.experiments[0].without_skill.status.value == "passed"
