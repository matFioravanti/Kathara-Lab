from pathlib import Path
from unittest.mock import Mock

import pytest

from kathara_pipeline.agent_runner import AgentRunner
from kathara_pipeline.correction_generator import CorrectionGenerator

from kathara_pipeline.exceptions import AgentExecutionError
from kathara_pipeline.models import CommandResult, ExperimentPaths, ResourceFiles, Variant, VariantPaths

_VALID_CORRECTION = (
    'lab_inline: |\n  r1[0]="A"\n  r2[0]="A"\n'
    'convergence_time: 10\n'
    'test:\n  requiring_startup: [r1, r2]\n'
    '  ip_mapping:\n    r1: {eth0: 10.0.0.1/24}\n    r2: {eth0: 10.0.0.2/24}\n'
    '  reachability:\n    r1: [10.0.0.2]\n    r2: [10.0.0.1]\n'
)


def _make_resources(tmp_path: Path) -> ResourceFiles:
    skill = tmp_path / "SKILL.md"
    schema = tmp_path / "config-schema.md"
    skill.write_text("skill")
    schema.write_text("schema")
    resources = Mock(spec=ResourceFiles)
    resources.checker_skill = skill
    resources.checker_schema = schema
    return resources


def _make_runner(return_code: int = 0) -> Mock:
    runner = Mock(spec=AgentRunner)
    runner.provider = "mock-provider"
    return runner


def _make_cmd_result(duration: float = 1.0, return_code: int = 0) -> CommandResult:
    return CommandResult(["mock"], return_code, "", "", duration, False)


# ------------------------------------------------------------------ #
# Existing standalone / retry tests                                   #
# ------------------------------------------------------------------ #

def test_correction_generator_retry_keeps_file_and_modifies_instruction(tmp_path: Path):
    runner = _make_runner()
    experiment_paths = Mock(spec=ExperimentPaths)

    variant_paths = Mock(spec=VariantPaths)
    variant_paths.correction_workspace = tmp_path / "correction_workspace"
    variant_paths.correction_logs = tmp_path / "logs"
    variant_paths.correction_dir = tmp_path / "correction_dir"
    variant_paths.correction = variant_paths.correction_dir / "correction.yaml"
    variant_paths.source = tmp_path / "source"
    variant_paths.source.mkdir()

    resources = _make_resources(tmp_path)

    def mock_run(*args, **kwargs):
        output_dir = variant_paths.correction_workspace / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        correction_file = output_dir / "correction.yaml"

        attempt = 1 if not hasattr(mock_run, 'called_once') else 2
        mock_run.called_once = True

        if attempt == 1:
            correction_file.write_text("metadata:\n  retry_test_marker: preserve-me\n")
            return _make_cmd_result(return_code=1)
        else:
            assert correction_file.exists(), "correction.yaml was wiped before attempt 2!"
            assert "preserve-me" in correction_file.read_text(), "sentinel not found in correction.yaml!"
            correction_file.write_text("lab_inline: |\n  r1[0]=A\n")
            return _make_cmd_result(return_code=0)

    runner.run.side_effect = mock_run



    generator = CorrectionGenerator(runner=runner, timeout_seconds=10)
    result = generator.generate_with_retry(
        experiment_paths=experiment_paths,
        variant_paths=variant_paths,
        prompt_text="prompt",
        resources=resources,
    )

    assert result.success
    assert result.last_command_result.return_code == 0
    assert runner.run.call_count == 2

    second_call_kwargs = runner.run.call_args_list[1].kwargs
    instruction = second_call_kwargs["instruction"]
    assert "Open the existing output/correction.yaml and correct in-place" in instruction
    assert "execution failed" in instruction
    assert "Preserve all valid sections already present" in instruction
    assert "Do not regenerate the entire correction from scratch" in instruction

    input_dir = variant_paths.correction_workspace / "input"
    assert (input_dir / "prompt.md").is_file()
    assert not (input_dir / "evaluation-plan.yaml").exists()
    assert not (input_dir / "evaluation-spec.md").exists()
    assert not (input_dir / "check-plan.md").exists()


# ------------------------------------------------------------------ #
# Paired generation tests                                             #
# ------------------------------------------------------------------ #

def _make_paired_setup(tmp_path: Path):
    """Return (generator, experiment_paths, with_paths, without_paths, resources)."""
    runner = _make_runner()
    runner.provider = "mock-provider"

    experiment_paths = Mock(spec=ExperimentPaths)
    experiment_paths.root = tmp_path / "experiment"
    experiment_paths.root.mkdir(parents=True)

    def _vp(name: str) -> VariantPaths:
        vp = Mock(spec=VariantPaths)
        vp.source = tmp_path / name / "source"
        vp.source.mkdir(parents=True)
        (vp.source / "lab.conf").write_text(f"r1[0]={name}\n")
        vp.correction_dir = tmp_path / name / "correction"
        vp.correction = vp.correction_dir / "correction.yaml"
        return vp

    with_paths = _vp("with_skill")
    without_paths = _vp("without_skill")
    resources = _make_resources(tmp_path)
    generator = CorrectionGenerator(runner=runner, timeout_seconds=10)
    return runner, generator, experiment_paths, with_paths, without_paths, resources


def test_generate_pair_single_agent_call(tmp_path: Path):
    """Both labs valid → runner.run() called exactly once."""
    runner, generator, experiment_paths, with_paths, without_paths, resources = _make_paired_setup(tmp_path)

    def mock_run(*args, **kwargs):
        ws = kwargs["workspace"]
        (ws / "output" / "with_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "without_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "with_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        (ws / "output" / "without_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        kwargs["stdout_log"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["stdout_log"].write_text("{}\n")
        kwargs["stderr_log"].write_text("")
        return _make_cmd_result(duration=42.0)

    runner.run.side_effect = mock_run



    result = generator.generate_pair(
        experiment_paths=experiment_paths,
        with_skill_paths=with_paths,
        without_skill_paths=without_paths,
        prompt_text="prompt",
        resources=resources,
    )

    assert runner.run.call_count == 1, "Expected exactly one agent call for paired generation"
    assert result.with_skill_valid
    assert result.without_skill_valid
    assert result.duration_seconds == 42.0


def test_generate_pair_produces_two_corrections(tmp_path: Path):
    """generate_pair copies both correction.yaml to the final paths."""
    runner, generator, experiment_paths, with_paths, without_paths, resources = _make_paired_setup(tmp_path)

    def mock_run(*args, **kwargs):
        ws = kwargs["workspace"]
        (ws / "output" / "with_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "without_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "with_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        (ws / "output" / "without_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        kwargs["stdout_log"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["stdout_log"].write_text("{}\n")
        kwargs["stderr_log"].write_text("")
        return _make_cmd_result()

    runner.run.side_effect = mock_run



    generator.generate_pair(
        experiment_paths=experiment_paths,
        with_skill_paths=with_paths,
        without_skill_paths=without_paths,
        prompt_text="prompt",
        resources=resources,
    )

    assert with_paths.correction.is_file(), "with_skill correction.yaml not produced"
    assert without_paths.correction.is_file(), "without_skill correction.yaml not produced"



def test_generate_pair_is_independent(tmp_path: Path):
    """generate_pair is independent."""
    runner, generator, experiment_paths, with_paths, without_paths, resources = _make_paired_setup(tmp_path)
    captured_instructions: list[str] = []

    def mock_run(*args, **kwargs):
        captured_instructions.append(kwargs["instruction"])
        ws = kwargs["workspace"]
        (ws / "output" / "with_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "without_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "with_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        (ws / "output" / "without_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        kwargs["stdout_log"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["stdout_log"].write_text("{}\n")
        kwargs["stderr_log"].write_text("")
        return _make_cmd_result()

    runner.run.side_effect = mock_run



    generator.generate_pair(
        experiment_paths=experiment_paths,
        with_skill_paths=with_paths,
        without_skill_paths=without_paths,
        prompt_text="prompt",
        resources=resources,
    )

    assert len(captured_instructions) == 1
    instr = captured_instructions[0]
    assert "evaluation requirements" not in instr, "paired instruction must not mention 'evaluation requirements'"
    assert "Read input/prompt.md to understand what must be tested" in instr


def test_generate_pair_shared_log_path(tmp_path: Path):
    """Log files for paired call must be inside .workspaces/correction_paired/logs/."""
    runner, generator, experiment_paths, with_paths, without_paths, resources = _make_paired_setup(tmp_path)
    captured_log_paths: list[Path] = []

    def mock_run(*args, **kwargs):
        captured_log_paths.append(kwargs["stdout_log"])
        ws = kwargs["workspace"]
        (ws / "output" / "with_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "without_skill").mkdir(parents=True, exist_ok=True)
        (ws / "output" / "with_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        (ws / "output" / "without_skill" / "correction.yaml").write_text(_VALID_CORRECTION)
        kwargs["stdout_log"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["stdout_log"].write_text("{}\n")
        kwargs["stderr_log"].write_text("")
        return _make_cmd_result()

    runner.run.side_effect = mock_run



    generator.generate_pair(
        experiment_paths=experiment_paths,
        with_skill_paths=with_paths,
        without_skill_paths=without_paths,
        prompt_text="prompt",
        resources=resources,
    )

    assert len(captured_log_paths) == 1
    log_path = captured_log_paths[0]
    # Log must be inside correction_paired/logs/, NOT inside variant correction dirs
    assert "correction_paired" in str(log_path), f"Log not in correction_paired/: {log_path}"
    assert "with_skill" not in str(log_path.parent), f"Log wrongly placed in variant dir: {log_path}"
    assert "without_skill" not in str(log_path.parent), f"Log wrongly placed in variant dir: {log_path}"


def test_generate_standalone_single_valid_lab(tmp_path: Path):
    """generate_with_retry (standalone) is used when only one lab is valid; no paired call."""
    runner = _make_runner()
    runner.provider = "mock-provider"

    experiment_paths = Mock(spec=ExperimentPaths)

    # Use real paths so shutil operations inside generate_with_retry work
    variant_paths = Mock(spec=VariantPaths)
    variant_paths.correction_workspace = tmp_path / "standalone_ws"
    variant_paths.correction_logs = tmp_path / "standalone_logs"
    variant_paths.correction_dir = tmp_path / "standalone_correction"
    variant_paths.correction = variant_paths.correction_dir / "correction.yaml"
    variant_paths.source = tmp_path / "standalone_source"
    variant_paths.source.mkdir(parents=True)
    (variant_paths.source / "lab.conf").write_text("r1[0]=A\n")

    resources = _make_resources(tmp_path)
    correction_instructions: list[str] = []

    def mock_run(*args, **kwargs):
        instr = kwargs["instruction"]
        correction_instructions.append(instr)
        ws = kwargs["workspace"]
        out = ws / "output"
        out.mkdir(parents=True, exist_ok=True)
        (out / "correction.yaml").write_text(_VALID_CORRECTION)
        kwargs["stdout_log"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["stdout_log"].write_text("{}\n")
        kwargs["stderr_log"].write_text("")
        return _make_cmd_result()

    runner.run.side_effect = mock_run



    generator = CorrectionGenerator(runner=runner, timeout_seconds=10)

    # Standalone: generate_with_retry for a single variant
    result = generator.generate_with_retry(
        experiment_paths=experiment_paths,
        variant_paths=variant_paths,
        prompt_text="prompt",
        resources=resources,
    )

    assert runner.run.call_count == 1
    assert result.success
    # Must be a standalone instruction (not paired)
    assert "candidates/with_skill" not in correction_instructions[0], \
        "Standalone call must not use paired workspace layout"
    assert "candidates/without_skill" not in correction_instructions[0], \
        "Standalone call must not use paired workspace layout"

