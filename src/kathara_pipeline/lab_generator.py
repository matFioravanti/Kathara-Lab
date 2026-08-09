from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .exceptions import AgentExecutionError
from .models import CommandResult, ResourceFiles, Variant, VariantPaths
from .lab_validator import LabValidator

MAX_LAB_ATTEMPTS = 2


class LabGenerator:
    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction(variant: Variant) -> str:
        if variant is Variant.WITH_SKILL:
            return (
                "Read input/prompt.md and resources/creation/SKILL.md. "
                "Use resources/creation/SKILL.md as the authoritative general implementation guide for Kathara, "
                "while the requested scenario itself is defined only by input/prompt.md. "
                "Generate exactly one complete Kathara laboratory inside output/lab/. "
                "Do not read files outside this workspace. Do not modify input/ or resources/. "
                "Do not generate correction.yaml and do not run Kathara or kathara_lab_checker. "
                "The laboratory must be complete, persistent, contain no placeholders, and be internally consistent."
            )
        return (
            "Read only input/prompt.md. Generate exactly one complete Kathara laboratory inside output/lab/. "
            "Do not read files outside this workspace. No creation Skill or external implementation guide is available. "
            "Do not modify input/prompt.md. Do not generate correction.yaml and do not run Kathara or kathara_lab_checker. "
            "The laboratory must be complete, persistent, contain no placeholders, and be internally consistent."
        )

    @staticmethod
    def retry_instruction(variant: Variant, validation_errors: tuple[str, ...]) -> str:
        errors_text = "\n".join(f"  - {e}" for e in validation_errors)
        base = LabGenerator.instruction(variant)
        return (
            "The previously generated output/lab failed static validation with the following errors:\n"
            f"{errors_text}\n\n"
            f"Fix all the errors above. {base}"
        )

    def prepare_workspace(
        self,
        *,
        paths: VariantPaths,
        prompt_text: str,
        variant: Variant,
        resources: ResourceFiles,
    ) -> None:
        if paths.workspace.exists():
            shutil.rmtree(paths.workspace)
        (paths.workspace / "input").mkdir(parents=True)
        (paths.workspace / "output").mkdir()
        (paths.workspace / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")
        if variant is Variant.WITH_SKILL:
            target = paths.workspace / "resources" / "creation"
            target.mkdir(parents=True)
            shutil.copy2(resources.creation_skill, target / "SKILL.md")

    def _run_attempt(
        self,
        *,
        paths: VariantPaths,
        instruction: str,
        attempt: int,
    ) -> CommandResult:
        generated = paths.workspace / "output" / "lab"
        if generated.exists():
            shutil.rmtree(generated)
        result = self.runner.run(
            instruction=instruction,
            workspace=paths.workspace,
            output_last_message=paths.workspace / ".agent-last-message.txt",
            stdout_log=paths.logs / f"{self.runner.provider}-lab-attempt{attempt}.jsonl",
            stderr_log=paths.logs / f"{self.runner.provider}-lab-attempt{attempt}.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )
        if result.return_code != 0 or result.timed_out:
            raise AgentExecutionError(
                f"{self.runner.provider} lab generation failed (return code {result.return_code}, attempt {attempt})"
            )
        if not generated.is_dir():
            raise AgentExecutionError(
                f"{self.runner.provider} completed without creating output/lab/ (attempt {attempt})"
            )
        return result

    def generate_with_retry(
        self,
        *,
        paths: VariantPaths,
        prompt_text: str,
        variant: Variant,
        resources: ResourceFiles,
        validator: LabValidator,
    ) -> CommandResult:
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, variant=variant, resources=resources)
        paths.logs.mkdir(parents=True, exist_ok=True)
        
        last_result: CommandResult | None = None
        last_errors: tuple[str, ...] = ()
        
        for attempt in range(1, MAX_LAB_ATTEMPTS + 1):
            if attempt == 1:
                instruction = self.instruction(variant)
            else:
                instruction = self.retry_instruction(variant, last_errors)
                
            last_result = self._run_attempt(paths=paths, instruction=instruction, attempt=attempt)
            
            generated = paths.workspace / "output" / "lab"
            validation = validator.validate(generated, prompt_text)
            if validation.valid:
                if paths.source.exists():
                    shutil.rmtree(paths.source)
                if paths.source_failed.exists():
                    shutil.rmtree(paths.source_failed)
                shutil.copytree(generated, paths.source, symlinks=True)
                return last_result
                
            last_errors = validation.errors
            
        if paths.source_failed.exists():
            shutil.rmtree(paths.source_failed)
        if generated.exists():
            shutil.copytree(generated, paths.source_failed, symlinks=True)
            
        raise AgentExecutionError(
            f"Generated lab still invalid after {MAX_LAB_ATTEMPTS} attempt(s): "
            + "; ".join(last_errors)
        )
