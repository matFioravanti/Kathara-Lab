from pathlib import Path
from unittest.mock import Mock

import pytest

from kathara_pipeline.exceptions import AgentExecutionError
from kathara_pipeline.lab_generator import LabGenerator
from kathara_pipeline.lab_validator import LabValidator
from kathara_pipeline.models import CommandResult, ResourceFiles, Variant, VariantPaths


def test_retry_after_lab_validator_failure(tmp_path: Path):
    runner = Mock()
    def side_effect(*args, **kwargs):
        workspace = kwargs["workspace"]
        attempt_file = workspace / "attempt.txt"
        attempt = 1 if not attempt_file.exists() else 2
        attempt_file.write_text(str(attempt))

        generated = workspace / "output" / "lab"
        generated.mkdir(parents=True, exist_ok=True)
        if attempt == 1:
            # A placeholder token will cause the new sanity validator to reject this lab
            (generated / "lab.conf").write_text('r1[0]="A"\nTODO: fix routing\n')
            (generated / "KEEP_ME.txt").write_text("sentinel")
        else:
            # Physically verify the sentinel exists BEFORE doing anything
            assert (generated / "KEEP_ME.txt").exists(), "output/lab/ was wiped before attempt 2!"
            assert (generated / "KEEP_ME.txt").read_text() == "sentinel"

            (generated / "lab.conf").write_text('r1[0]="A"\n')

        return CommandResult(
            command=("agent",),
            return_code=0,
            duration_seconds=1.0,
            timed_out=False,
            stdout="",
            stderr="",
        )

    runner.run.side_effect = side_effect

    generator = LabGenerator(runner, timeout_seconds=10)
    validator = LabValidator()
    
    paths = VariantPaths(
        root=tmp_path / "root",
        labs_dir=tmp_path / "labs",
        workspace=tmp_path / "workspace",
        source=tmp_path / "source",
        source_failed=tmp_path / "source_failed",
        candidate=tmp_path / "candidate",
        correction_workspace=tmp_path / "correction_workspace",
        correction_dir=tmp_path / "correction",
        correction=tmp_path / "correction" / "correction.yaml",
        checker_run=tmp_path / "checker_run",
        reports=tmp_path / "reports",
        manifest=tmp_path / "manifest.json",
        logs=tmp_path / "logs",
        correction_logs=tmp_path / "correction_logs",
    )
    
    resources = ResourceFiles(
        root=tmp_path / "resources",
        creation_skill=tmp_path / "creation.md",
        checker_skill=tmp_path / "checker.md",
        checker_schema=tmp_path / "schema.md",
        creation_skill_hash="a",
        checker_skill_hash="b",
        checker_schema_hash="c",
    )
    for p in (resources.creation_skill, resources.checker_skill, resources.checker_schema):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("test")
        
    result = generator.generate_with_retry(
        paths=paths,
        prompt_text="test",
        variant=Variant.WITH_SKILL,
        resources=resources,
        validator=validator,
    )
    
    assert result.success
    assert result.last_command_result.return_code == 0
    assert runner.run.call_count == 2
    
    # Assert second run used the retry instruction
    second_call_instruction = runner.run.call_args_list[1].kwargs["instruction"]
    assert "failed static validation with the following errors" in second_call_instruction
    assert "modify it in-place" in second_call_instruction
    assert "Preserve every valid part" in second_call_instruction
    assert "Do not rebuild unrelated files" in second_call_instruction


def test_final_invalid_lab_is_preserved_in_source_failed(tmp_path: Path):
    runner = Mock()
    # Mock runner.run to simulate agent generating an invalid lab on ALL attempts
    def side_effect(*args, **kwargs):
        workspace = kwargs["workspace"]
        generated = workspace / "output" / "lab"
        generated.mkdir(parents=True, exist_ok=True)
        # A placeholder token makes the new sanity validator reject this lab on every attempt
        (generated / "lab.conf").write_text('r1[0]="A"\nTODO: fix routing\n')

        return CommandResult(
            command=("agent",),
            return_code=0,
            duration_seconds=1.0,
            timed_out=False,
            stdout="",
            stderr="",
        )

    runner.run.side_effect = side_effect

    generator = LabGenerator(runner, timeout_seconds=10)
    validator = LabValidator()
    
    paths = VariantPaths(
        root=tmp_path / "root",
        labs_dir=tmp_path / "labs",
        workspace=tmp_path / "workspace",
        source=tmp_path / "source",
        source_failed=tmp_path / "source_failed",
        candidate=tmp_path / "candidate",
        correction_workspace=tmp_path / "correction_workspace",
        correction_dir=tmp_path / "correction",
        correction=tmp_path / "correction" / "correction.yaml",
        checker_run=tmp_path / "checker_run",
        reports=tmp_path / "reports",
        manifest=tmp_path / "manifest.json",
        logs=tmp_path / "logs",
        correction_logs=tmp_path / "correction_logs",
    )
    
    resources = ResourceFiles(
        root=tmp_path / "resources",
        creation_skill=tmp_path / "creation.md",
        checker_skill=tmp_path / "checker.md",
        checker_schema=tmp_path / "schema.md",
        creation_skill_hash="a",
        checker_skill_hash="b",
        checker_schema_hash="c",
    )
    for p in (resources.creation_skill, resources.checker_skill, resources.checker_schema):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("test")
        
    from kathara_pipeline.exceptions import GenerationError
    with pytest.raises(GenerationError, match="Generated lab still invalid"):
        generator.generate_with_retry(
            paths=paths,
            prompt_text="test",
            variant=Variant.WITH_SKILL,
            resources=resources,
            validator=validator,
        )
        
    assert runner.run.call_count == 2
    
    assert paths.source_failed.exists()
    assert "TODO" in (paths.source_failed / "lab.conf").read_text()
    assert not paths.source.exists()



