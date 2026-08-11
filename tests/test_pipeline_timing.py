from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock

from kathara_pipeline.config import load_config
from kathara_pipeline.models import CommandResult, Variant
from kathara_pipeline.pipeline import Pipeline
from kathara_pipeline.paths import build_experiment_paths
from kathara_pipeline.resource_discovery import discover_resources
import shutil

_VALID_CORRECTION = (
    'lab_inline: |\n  r1[0]="A"\n  r2[0]="A"\n'
    'convergence_time: 10\n'
    'test:\n  requiring_startup: [r1, r2]\n'
    '  ip_mapping:\n    r1: {eth0: 10.0.0.1/24}\n    r2: {eth0: 10.0.0.2/24}\n'
    '  reachability:\n    r1: [10.0.0.2]\n    r2: [10.0.0.1]\n'
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
    out.mkdir(parents=True, exist_ok=True)
    (out / "lab.conf").write_text(_VALID_LAB[0], encoding="utf-8")
    (out / "r1.startup").write_text(_VALID_LAB[1], encoding="utf-8")
    (out / "r2.startup").write_text(_VALID_LAB[2], encoding="utf-8")
class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def get_time(self):
        return self.t

    def advance(self, seconds: float):
        self.t += seconds


class TimingFakeRunner:
    provider = "fake"
    model = "same-model"
    reasoning_effort = "same-effort"

    def __init__(self, clock: FakeClock):
        self.clock = clock

    def build_command(self, *, instruction, workspace, output_last_message):
        return ("fake", instruction)

    def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
        out = workspace / "output"
        out.mkdir(parents=True, exist_ok=True)

        if "EXACTLY THREE files" in instruction:
            self.clock.advance(80.0) # evaluation plan duration
            (out / "evaluation-spec.md").write_text("Dummy", encoding="utf-8")
            (out / "check-plan.md").write_text("Dummy", encoding="utf-8")
            (out / "evaluation-plan.yaml").write_text("checks:\n  - id: chk1\n    checker: reachability\n", encoding="utf-8")
            duration = 80.0
        elif "binding an already-defined" in instruction or "failed validation" in instruction or "validated reference correction" in instruction:
            self.clock.advance(40.0) # correction duration
            (out / "correction.yaml").write_text(_VALID_CORRECTION, encoding="utf-8")
            duration = 40.0
        else:
            # lab generation
            if "WITHOUT" in str(workspace) or "without_skill" in str(workspace):
                self.clock.advance(130.0) # without_skill duration
                duration = 130.0
            else:
                self.clock.advance(100.0) # with_skill duration
                duration = 100.0
            _write_lab(workspace)

        stdout_log.parent.mkdir(parents=True, exist_ok=True)
        stdout_log.write_text("{}\n", encoding="utf-8")
        stderr_log.write_text("", encoding="utf-8")
        return CommandResult(("fake",), 0, "", "", duration, False)


def test_pipeline_timing_sequential(tmp_path: Path, monkeypatch):
    clock = FakeClock()
    monkeypatch.setattr(time, "perf_counter", clock.get_time)
    monkeypatch.setattr(time, "monotonic", clock.get_time)

    project, prompts_dir = _make_project(tmp_path)
    
    def mock_build_runner(*args, **kwargs):
        return TimingFakeRunner(clock)
    
    monkeypatch.setattr("kathara_pipeline.pipeline.build_runner", mock_build_runner)

    config = load_config(project / "pipeline.yaml")
    from dataclasses import replace
    config = replace(config, processing=replace(config.processing, parallel_variants=False))
    
    pipeline = Pipeline(config)
    prompts = pipeline.discover(prompts_dir)
    resources = discover_resources(project / "resources")
    
    # Mock CheckerRunner to advance clock
    original_checker_run = pipeline.checker.run
    def mock_checker_run(*args, **kwargs):
        clock.advance(25.0)
        res = original_checker_run(*args, **kwargs)
        return CommandResult(res.command, res.return_code, res.stdout, res.stderr, 25.0, res.timed_out)
    monkeypatch.setattr(pipeline.checker, "run", mock_checker_run)

    summary = pipeline.run(prompts, resources)

    assert len(summary.experiments) == 1
    exp = summary.experiments[0]

    # Verify timing values
    assert exp.timings["evaluation_plan_seconds"] >= 80.0
    # Sequential: 100.0 + 130.0 = 230.0
    assert exp.timings["lab_generation_wall_seconds"] >= 230.0
    assert "parallel_lab_generation_wall_seconds" not in exp.timings
    
    # Check durations matched in variants
    assert exp.with_skill.lab_duration_seconds == 100.0
    assert exp.without_skill.lab_duration_seconds == 130.0
    assert exp.with_skill.correction_duration_seconds == 40.0
    assert exp.without_skill.correction_duration_seconds == 40.0
    assert exp.with_skill.checker_duration_seconds == 25.0
    assert exp.without_skill.checker_duration_seconds == 25.0

    assert exp.timings["corrections_wall_seconds"] >= 80.0
    assert exp.timings["checkers_wall_seconds"] >= 50.0
    assert exp.timings["pipeline_overhead_seconds"] >= 0.0

    # Ensure run_total_wall_seconds is recorded
    assert summary.run_total_wall_seconds > 0.0
    
    # Check pipeline-summary.json
    summary_file = config.paths.output / "pipeline-summary.json"
    data = json.loads(summary_file.read_text())
    assert "run_total_wall_seconds" in data
    
    # Check experiment summary json structure
    exp_dir = config.paths.output / prompts[0].experiment_id
    with_manifest = json.loads((exp_dir / "with_skill" / "manifest.json").read_text())
    assert with_manifest["generation"]["duration_seconds"] == 100.0
    assert with_manifest["correction_generation"]["duration_seconds"] == 40.0


def test_pipeline_timing_parallel(tmp_path: Path, monkeypatch):
    clock = FakeClock()
    
    # In a multithreaded test, a shared clock fake might be non-deterministic if we just advance it.
    # However, since they run in ThreadPoolExecutor, we can simulate wall clock parallel time.
    # We will use real time but very short sleep (e.g. 0.1 and 0.13) to ensure tests don't take forever.
    
    def mock_build_runner(*args, **kwargs):
        class RealSleepRunner:
            provider = "fake"
            model = "same-model"
            reasoning_effort = "same-effort"
            def build_command(self, *, instruction, workspace, output_last_message):
                return ("fake", instruction)
            def run(self, *, instruction, workspace, output_last_message, stdout_log, stderr_log, timeout_seconds):
                if "EXACTLY THREE files" in instruction:
                    time.sleep(0.08)
                    out = workspace / "output"
                    out.mkdir(parents=True, exist_ok=True)
                    (out / "evaluation-spec.md").write_text("Dummy", encoding="utf-8")
                    (out / "check-plan.md").write_text("Dummy", encoding="utf-8")
                    (out / "evaluation-plan.yaml").write_text("checks:\n  - id: chk1\n    checker: reachability\n", encoding="utf-8")
                    return CommandResult(("fake",), 0, "", "", 0.08, False)
                elif "binding an already-defined" in instruction or "failed validation" in instruction or "validated reference correction" in instruction:
                    time.sleep(0.04)
                    out = workspace / "output"
                    out.mkdir(parents=True, exist_ok=True)
                    (out / "correction.yaml").write_text(_VALID_CORRECTION, encoding="utf-8")
                    duration = 0.04
                else:
                    if "WITHOUT" in str(workspace) or "without_skill" in str(workspace):
                        time.sleep(0.13)
                        duration = 0.13
                    else:
                        time.sleep(0.10)
                        duration = 0.10
                    _write_lab(workspace)
                stdout_log.parent.mkdir(parents=True, exist_ok=True)
                stdout_log.write_text("{}\n", encoding="utf-8")
                stderr_log.write_text("", encoding="utf-8")
                return CommandResult(("fake",), 0, "", "", duration, False)
        return RealSleepRunner()

    monkeypatch.setattr("kathara_pipeline.pipeline.build_runner", mock_build_runner)

    project, prompts_dir = _make_project(tmp_path)
    config = load_config(project / "pipeline.yaml")
    from dataclasses import replace
    config = replace(config, processing=replace(config.processing, parallel_variants=True))
    
    pipeline = Pipeline(config)
    prompts = pipeline.discover(prompts_dir)
    resources = discover_resources(project / "resources")

    original_checker_run = pipeline.checker.run
    def mock_checker_run(*args, **kwargs):
        time.sleep(0.02)
        res = original_checker_run(*args, **kwargs)
        return CommandResult(res.command, res.return_code, res.stdout, res.stderr, 0.02, res.timed_out)
    monkeypatch.setattr(pipeline.checker, "run", mock_checker_run)

    summary = pipeline.run(prompts, resources)
    exp = summary.experiments[0]

    # Max of the two threads plus small overhead
    assert 0.12 <= exp.timings["lab_generation_wall_seconds"] <= 0.25
    assert 0.12 <= exp.timings["parallel_lab_generation_wall_seconds"] <= 0.25
    
    assert exp.timings["pipeline_overhead_seconds"] >= 0.0
