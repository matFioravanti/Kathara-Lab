from pathlib import Path
from unittest.mock import Mock

import pytest

from kathara_pipeline.agent_runner import AgentRunner
from kathara_pipeline.evaluation_plan_generator import EvaluationPlanGenerator
from kathara_pipeline.exceptions import AgentExecutionError
from kathara_pipeline.models import CommandResult, ExperimentPaths, ResourceFiles


def test_evaluation_plan_generator_success(tmp_path: Path):
    runner = Mock(spec=AgentRunner)
    runner.provider = "mock-provider"
    
    # Simulate agent generating both files
    def mock_run(*args, **kwargs):
        workspace = kwargs["workspace"]
        (workspace / "output").mkdir(exist_ok=True)
        (workspace / "output" / "evaluation-spec.md").write_text("spec")
        (workspace / "output" / "check-plan.md").write_text("plan")
        (workspace / "output" / "evaluation-plan.yaml").write_text("checks:\n  - id: '1'\n    checker: r")
        return CommandResult(
            command=["mock"],
            return_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
            timed_out=False,
        )
    runner.run.side_effect = mock_run

    paths = Mock(spec=ExperimentPaths)
    paths.evaluation_plan_workspace = tmp_path / "workspace"
    paths.evaluation_plan_logs = tmp_path / "logs"
    paths.evaluation_spec = tmp_path / "evaluation-spec.md"
    paths.check_plan = tmp_path / "check-plan.md"
    paths.structured_plan = tmp_path / "evaluation-plan.yaml"

    resources = Mock(spec=ResourceFiles)
    resources.creation_skill = tmp_path / "c_skill"
    resources.checker_skill = tmp_path / "ck_skill"
    resources.checker_schema = tmp_path / "schema"
    for p in (resources.creation_skill, resources.checker_skill, resources.checker_schema):
        p.write_text("data")

    generator = EvaluationPlanGenerator(runner=runner, timeout_seconds=10)
    
    result = generator.generate(paths=paths, prompt_text="prompt", resources=resources)
    assert result.return_code == 0
    assert paths.evaluation_spec.read_text() == "spec"
    assert paths.check_plan.read_text() == "plan"
    assert "checks:" in paths.structured_plan.read_text()


def test_evaluation_plan_generator_missing_file_raises_error(tmp_path: Path):
    runner = Mock(spec=AgentRunner)
    runner.provider = "mock-provider"
    
    # Simulate agent generating only one file
    def mock_run(*args, **kwargs):
        workspace = kwargs["workspace"]
        (workspace / "output").mkdir(exist_ok=True)
        (workspace / "output" / "evaluation-spec.md").write_text("spec")
        (workspace / "output" / "check-plan.md").write_text("plan")
        # Missing evaluation-plan.yaml
        return CommandResult(
            command=["mock"],
            return_code=0,
            stdout="",
            stderr="",
            duration_seconds=1.0,
            timed_out=False,
        )
    runner.run.side_effect = mock_run

    paths = Mock(spec=ExperimentPaths)
    paths.evaluation_plan_workspace = tmp_path / "workspace"
    paths.evaluation_plan_logs = tmp_path / "logs"
    paths.evaluation_spec = tmp_path / "evaluation-spec.md"
    paths.check_plan = tmp_path / "check-plan.md"
    paths.structured_plan = tmp_path / "evaluation-plan.yaml"

    resources = Mock(spec=ResourceFiles)
    resources.creation_skill = tmp_path / "c_skill"
    resources.checker_skill = tmp_path / "ck_skill"
    resources.checker_schema = tmp_path / "schema"
    for p in (resources.creation_skill, resources.checker_skill, resources.checker_schema):
        p.write_text("data")

    generator = EvaluationPlanGenerator(runner=runner, timeout_seconds=10)
    
    with pytest.raises(AgentExecutionError, match="without creating: evaluation-plan.yaml"):
        generator.generate(paths=paths, prompt_text="prompt", resources=resources)
