from pathlib import Path
from unittest.mock import Mock

import pytest

from kathara_pipeline.agent_runner import AgentRunner
from kathara_pipeline.correction_generator import CorrectionGenerator
from kathara_pipeline.correction_validator import CorrectionValidator
from kathara_pipeline.exceptions import AgentExecutionError
from kathara_pipeline.models import CommandResult, ExperimentPaths, ResourceFiles, Variant, VariantPaths

def test_correction_generator_retry_keeps_file_and_modifies_instruction(tmp_path: Path):
    # Setup mocks and paths
    runner = Mock(spec=AgentRunner)
    runner.provider = "mock-provider"

    experiment_paths = Mock(spec=ExperimentPaths)

    variant_paths = Mock(spec=VariantPaths)
    variant_paths.correction_workspace = tmp_path / "correction_workspace"
    variant_paths.correction_logs = tmp_path / "logs"
    variant_paths.correction_dir = tmp_path / "correction_dir"
    variant_paths.correction = variant_paths.correction_dir / "correction.yaml"
    variant_paths.source = tmp_path / "source"
    variant_paths.source.mkdir()

    resources = Mock(spec=ResourceFiles)
    resources.checker_skill = tmp_path / "SKILL.md"
    resources.checker_schema = tmp_path / "config-schema.md"
    resources.checker_skill.write_text("skill")
    resources.checker_schema.write_text("schema")

    # Mock runner.run to create a dummy correction.yaml
    def mock_run(*args, **kwargs):
        output_dir = variant_paths.correction_workspace / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        correction_file = output_dir / "correction.yaml"

        attempt = 1 if not hasattr(mock_run, 'called_once') else 2
        mock_run.called_once = True

        if attempt == 1:
            correction_file.write_text("metadata:\n  retry_test_marker: preserve-me\n")
        else:
            # Physically verify the sentinel exists BEFORE doing anything
            assert correction_file.exists(), "correction.yaml was wiped before attempt 2!"
            assert "preserve-me" in correction_file.read_text(), "sentinel not found in correction.yaml!"
            correction_file.write_text("lab_inline: |\n  r1[0]=A\n")

        return CommandResult(
            command=["mock"],
            return_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
            timed_out=False,
        )
    runner.run.side_effect = mock_run

    validator = Mock(spec=CorrectionValidator)
    # First attempt fails validation, second succeeds
    validator.validate.side_effect = [
        Mock(valid=False, errors=("test error 1",)),
        Mock(valid=True, errors=())
    ]

    generator = CorrectionGenerator(runner=runner, timeout_seconds=10)

    result = generator.generate_with_retry(
        experiment_paths=experiment_paths,
        variant_paths=variant_paths,
        prompt_text="prompt",
        resources=resources,
        validator=validator,
    )

    assert result.success
    assert result.last_command_result.return_code == 0
    assert runner.run.call_count == 2

    # Verify the instruction passed to the second run contains the specific wording
    second_call_kwargs = runner.run.call_args_list[1].kwargs
    instruction = second_call_kwargs["instruction"]
    assert "Open the existing output/correction.yaml and correct in-place" in instruction
    assert "test error 1" in instruction
    assert "Preserve all valid sections already present" in instruction
    assert "Do not regenerate the entire correction from scratch" in instruction

    # Verify that the workspace has prompt.md instead of evaluation-plan.yaml
    input_dir = variant_paths.correction_workspace / "input"
    assert (input_dir / "prompt.md").is_file()
    assert not (input_dir / "evaluation-plan.yaml").exists()
    assert not (input_dir / "evaluation-spec.md").exists()
    assert not (input_dir / "check-plan.md").exists()
