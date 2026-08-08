from __future__ import annotations

import csv
import shutil
from pathlib import Path

from kathara_pipeline.config import load_config
from kathara_pipeline.models import CommandResult, Variant
from kathara_pipeline.paths import ensure_output_root
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
    """Return (project_dir, prompts_dir)."""
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
        if "canonical" in instruction or "mandatory" in instruction or "CRITICAL" in instruction:
            out = workspace / "output" / "correction.yaml"
            out.write_text(self.correction_yaml, encoding="utf-8")
        else:
            _write_lab(workspace)
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", 1.0, False)


class FakeRunnerRetryFix(FakeRunner):
    """First correction attempt omits lab_inline; retry produces a valid one."""

    def __init__(self):
        super().__init__()
        self._correction_attempts = 0

    def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
        self.calls.append((instruction, workspace))
        if "canonical" in instruction or "mandatory" in instruction or "CRITICAL" in instruction:
            self._correction_attempts += 1
            content = _VALID_CORRECTION if self._correction_attempts > 1 else _INVALID_CORRECTION_NO_LAB_INLINE
            out = workspace / "output" / "correction.yaml"
            out.write_text(content, encoding="utf-8")
        else:
            _write_lab(workspace)
        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", 1.0, False)


class FakeChecker:
    def __init__(self):
        self.corrections: list[bytes] = []
        self.order: list[str] = []

    def prepare_candidate(self, source, paths):
        if paths.checker_run.exists():
            shutil.rmtree(paths.checker_run)
        paths.labs_dir.mkdir(parents=True)
        shutil.copytree(source, paths.candidate)

    def run(self, *, correction, paths):
        self.corrections.append(Path(correction).read_bytes())
        self.order.append(paths.root.name)
        report = paths.checker_run / "results_summary.csv"
        report.write_text(
            "total_tests,passed_tests,failed_tests,pass_percentage\n3,3,0,100\n",
            encoding="utf-8",
        )
        return CommandResult(("checker",), 0, "", "", 2.0, False)

    def build_command(self, *, correction, paths):
        return ("checker", str(correction), str(paths.labs_dir))


# ---------------------------------------------------------------------------
# Original test – variants sequential, exact correction reuse
# ---------------------------------------------------------------------------

def test_pipeline_runs_variants_sequentially_and_reuses_exact_correction(tmp_path: Path):
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
    assert len(fake_runner.calls) == 3
    assert "resources/creation/SKILL.md" in fake_runner.calls[0][0]
    assert "Read only input/prompt.md" in fake_runner.calls[1][0]
    assert "canonical" in fake_runner.calls[2][0]
    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2 and fake_checker.corrections[0] == fake_checker.corrections[1]
    exp = summary.experiments[0]
    assert exp.with_skill.status.value == "passed"
    assert exp.without_skill.status.value == "passed"
    assert exp.comparison.value == "EQUAL"


# ---------------------------------------------------------------------------
# New regression: checker NOT called when correction is invalid
# ---------------------------------------------------------------------------

def test_checker_is_not_called_when_correction_is_invalid(tmp_path: Path):
    """If all correction attempts produce an invalid YAML (no lab_inline),
    the checker must never be invoked for either variant."""
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunner(correction_yaml=_INVALID_CORRECTION_NO_LAB_INLINE)
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)
    # Checker must never have been called.
    assert fake_checker.corrections == []
    assert fake_checker.order == []
    # Experiment must report a correction failure.
    exp = summary.experiments[0]
    assert not exp.correction_generated
    assert exp.with_skill.status.value == "error"
    assert exp.without_skill.status.value == "error"


# ---------------------------------------------------------------------------
# New regression: retry fixes a correction that initially misses lab_inline
# ---------------------------------------------------------------------------

def test_retry_fixes_correction_missing_lab_inline(tmp_path: Path):
    """The first attempt produces a correction without lab_inline;
    the retry must produce a valid one and the checker must proceed normally."""
    project, prompts = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    pipeline = Pipeline(config)
    fake_runner = FakeRunnerRetryFix()
    pipeline.runner = fake_runner
    pipeline.lab_generator.runner = fake_runner
    pipeline.correction_generator.runner = fake_runner
    fake_checker = FakeChecker()
    pipeline.checker = fake_checker
    resources = discover_resources(project / "resources")
    summary = pipeline.run(discover_prompts(prompts), resources)
    # The correction generator must have been called twice for the correction.
    correction_calls = [c for c, _ in fake_runner.calls if "canonical" in c or "CRITICAL" in c]
    assert len(correction_calls) == 2, f"Expected 2 correction attempts, got: {correction_calls}"
    # Checker ran for both variants using the same (repaired) correction.
    assert fake_checker.order == ["with_skill", "without_skill"]
    assert len(fake_checker.corrections) == 2
    assert fake_checker.corrections[0] == fake_checker.corrections[1]
    exp = summary.experiments[0]
    assert exp.correction_generated
    assert exp.with_skill.status.value == "passed"
    assert exp.without_skill.status.value == "passed"


# ---------------------------------------------------------------------------
# New regression: both variants always use the exact same canonical correction
# ---------------------------------------------------------------------------

def test_both_variants_use_same_canonical_correction(tmp_path: Path):
    """Regardless of how many correction attempts were needed, both variants
    must receive the identical canonical correction bytes."""
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
    pipeline.run(discover_prompts(prompts), resources)
    assert len(fake_checker.corrections) == 2
    assert fake_checker.corrections[0] == fake_checker.corrections[1], (
        "with_skill and without_skill must receive the exact same canonical correction"
    )
