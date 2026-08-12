from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .exceptions import AgentExecutionError
from .models import CommandResult, ResourceFiles, Variant, VariantPaths

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
        if variant is Variant.WITH_SKILL:
            base_rules = (
                "Read input/prompt.md and resources/creation/SKILL.md. "
                "Use resources/creation/SKILL.md as the authoritative general implementation guide for Kathara, "
                "while the requested scenario itself is defined only by input/prompt.md."
            )
        else:
            base_rules = (
                "Read only input/prompt.md. No creation Skill or external implementation guide is available."
            )
        
        return (
            "The previously generated output/lab/ failed with the following errors:\n"
            f"{errors_text}\n\n"
            "Read the existing output/lab directory and modify it in-place.\n"
            "Fix all validation errors listed above.\n"
            "Preserve every valid part of the current lab.\n"
            "Do not rebuild unrelated files.\n"
            "Do not recreate the entire lab unless the current structure makes the requested correction impossible.\n"
            "Do not generate correction.yaml and do not run Kathara or kathara_lab_checker.\n"
            "The laboratory must be complete, persistent, contain no placeholders, and be internally consistent.\n"
            f"{base_rules}"
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
        if attempt == 1 and generated.exists():
            shutil.rmtree(generated)
        return self.runner.run(
            instruction=instruction,
            workspace=paths.workspace,
            output_last_message=paths.workspace / ".agent-last-message.txt",
            stdout_log=paths.logs / f"{self.runner.provider}-lab-attempt{attempt}.jsonl",
            stderr_log=paths.logs / f"{self.runner.provider}-lab-attempt{attempt}.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )

    def generate_with_retry(
        self,
        *,
        paths: VariantPaths,
        prompt_text: str,
        variant: Variant,
        resources: ResourceFiles,
    ) -> "GenerationResult":
        from .models import GenerationAttempt, GenerationResult
        from .exceptions import GenerationError
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, variant=variant, resources=resources)
        paths.logs.mkdir(parents=True, exist_ok=True)
        
        last_result: CommandResult | None = None
        last_errors: tuple[str, ...] = ()
        attempts_log: list[GenerationAttempt] = []
        total_duration = 0.0
        
        for attempt in range(1, MAX_LAB_ATTEMPTS + 1):
            if attempt == 1:
                instruction = self.instruction(variant)
            else:
                instruction = self.retry_instruction(variant, last_errors)
                
            last_result = self._run_attempt(paths=paths, instruction=instruction, attempt=attempt)
            current_duration = last_result.duration_seconds
            current_code = last_result.return_code
            current_timeout = last_result.timed_out
            total_duration += current_duration
            
            generated = paths.workspace / "output" / "lab"
            
            if current_code != 0 or current_timeout:
                validation_errors = (f"{self.runner.provider} execution failed (return code {current_code}, timeout {current_timeout})",)
                valid = False
            elif not generated.is_dir():
                validation_errors = (f"{self.runner.provider} completed without creating output/lab/",)
                valid = False
            else:
                validation_errors = ()
                valid = True
            
            attempts_log.append(GenerationAttempt(
                attempt=attempt,
                duration_seconds=current_duration,
                return_code=current_code,
                timed_out=current_timeout,
                success=valid,
                validation_errors=validation_errors
            ))
            
            if valid:
                if paths.source.exists():
                    shutil.rmtree(paths.source)
                if paths.source_failed.exists():
                    shutil.rmtree(paths.source_failed)
                shutil.copytree(generated, paths.source, symlinks=True)
                return GenerationResult(
                    last_command_result=last_result,
                    calls=attempt,
                    retries=attempt - 1,
                    total_duration_seconds=total_duration,
                    attempts=tuple(attempts_log),
                    success=True
                )
                
            last_errors = validation_errors
            
        if paths.source_failed.exists():
            shutil.rmtree(paths.source_failed)
        if generated.exists():
            shutil.copytree(generated, paths.source_failed, symlinks=True)
            
        error_msg = f"Generated lab still invalid after {MAX_LAB_ATTEMPTS} attempt(s): " + "; ".join(last_errors)
        res = GenerationResult(
            last_command_result=last_result,
            calls=MAX_LAB_ATTEMPTS,
            retries=MAX_LAB_ATTEMPTS - 1,
            total_duration_seconds=total_duration,
            attempts=tuple(attempts_log),
            success=False
        )
        raise GenerationError(error_msg, res)
