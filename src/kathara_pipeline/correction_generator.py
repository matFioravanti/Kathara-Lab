from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .correction_validator import CorrectionValidator
from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, VariantPaths, ResourceFiles

MAX_CORRECTION_ATTEMPTS = 2


class CorrectionGenerator:
    """Generate one candidate-specific correction for the paired experiment."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Determine the evaluation requirements from the original prompt.\n"
            "Read input/prompt.md to understand what the network must achieve.\n"
            "Read candidate/ (the generated lab implementation) to resolve the concrete values "
            "needed to instantiate those requirements: device names, IP addresses, interfaces, "
            "routes, gateways, router IDs, topology references.\n\n"
            "Use resources/checker/SKILL.md and resources/checker/config-schema.md to produce "
            "a valid output/correction.yaml for kathara-lab-checker.\n\n"
            "IMPORTANT: lab_inline is mandatory and must contain the complete expected topology "
            "derived from the candidate lab. default_image is a mandatory checker field. "
            "Use lab_inline rather than structure and omit labs_path. "
            "Follow the runtime 0.1.14 compatibility rules in the Skill.\n"
            "Write only YAML to output/correction.yaml, with no surrounding prose. "
            "Do not create any other output file."
        )

    @staticmethod
    def adaptation_instruction() -> str:
        return (
            "output/correction.yaml is already a copy of the validated reference correction.\n"
            "Open it and modify it in place.\n"
            "Do not recreate the correction from scratch.\n"
            "Adapt only candidate-dependent concrete values.\n\n"
            "Read the current candidate/ lab and adapt values required for the checks to apply "
            "to this laboratory. For example: device names, IP addresses, interface identifiers, "
            "gateways, next hops, route destinations, collision domains, lab_inline, router IDs, "
            "default_image (if needed), etc.\n\n"
            "Do not redesign the evaluation strategy. "
            "Preserve the same semantic checks. Do not add or remove checks. "
            "The validated reference correction is authoritative for which checks must exist. "
            "Do not copy candidate-specific values from the reference correction when they "
            "do not match the current candidate.\n\n"
            "Write only YAML with no surrounding prose. Do not create any other output file."
        )

    @staticmethod
    def retry_instruction(validation_errors: tuple[str, ...]) -> str:
        errors_text = "\n".join(f"  - {e}" for e in validation_errors)
        return (
            "The previously generated output/correction.yaml failed validation with the following errors:\n"
            f"{errors_text}\n\n"
            "Open the existing output/correction.yaml and correct in-place only the reported errors. "
            "Preserve all valid sections already present in the file. Do not regenerate the entire correction from scratch.\n"
            "Read input/prompt.md, candidate/, resources/checker/SKILL.md, and resources/checker/config-schema.md again to guide your fixes.\n"
            "lab_inline is mandatory and must contain the complete expected topology (lab.conf format). It must be a non-empty string. "
            "Do not use structure. Do not include labs_path. "
            "Write only YAML to output/correction.yaml, with no surrounding prose. Do not create any other output file."
        )

    def prepare_workspace(
        self,
        *,
        experiment_paths: ExperimentPaths,
        variant_paths: VariantPaths,
        prompt_text: str,
        resources: ResourceFiles,
        reference_correction: Path | None = None,
    ) -> None:
        if variant_paths.correction_workspace.exists():
            shutil.rmtree(variant_paths.correction_workspace)
        (variant_paths.correction_workspace / "input").mkdir(parents=True)
        resource_dir = variant_paths.correction_workspace / "resources" / "checker"
        resource_dir.mkdir(parents=True)
        (variant_paths.correction_workspace / "output").mkdir()

        # Write the original prompt so the LLM can determine evaluation requirements
        (variant_paths.correction_workspace / "input" / "prompt.md").write_text(
            prompt_text, encoding="utf-8"
        )

        if reference_correction is not None:
            shutil.copy2(reference_correction, variant_paths.correction_workspace / "output" / "correction.yaml")

        shutil.copytree(variant_paths.source, variant_paths.correction_workspace / "candidate")

        shutil.copy2(resources.checker_skill, resource_dir / "SKILL.md")
        shutil.copy2(resources.checker_schema, resource_dir / "config-schema.md")

    def _run_attempt(
        self,
        *,
        variant_paths: VariantPaths,
        instruction: str,
        attempt: int,
    ) -> CommandResult:
        """Run one agent call."""
        return self.runner.run(
            instruction=instruction,
            workspace=variant_paths.correction_workspace,
            output_last_message=variant_paths.correction_workspace / ".agent-last-message.txt",
            stdout_log=variant_paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.jsonl",
            stderr_log=variant_paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )

    def generate(self, *, experiment_paths: ExperimentPaths, variant_paths: VariantPaths, prompt_text: str, resources: ResourceFiles) -> CommandResult:
        """Single-attempt generation (kept for backward compatibility)."""
        self.prepare_workspace(experiment_paths=experiment_paths, variant_paths=variant_paths, prompt_text=prompt_text, resources=resources)
        variant_paths.correction_logs.mkdir(parents=True, exist_ok=True)
        result = self._run_attempt(variant_paths=variant_paths, instruction=self.instruction(), attempt=1)
        variant_paths.correction_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(variant_paths.correction_workspace / "output" / "correction.yaml", variant_paths.correction)
        return result

    def generate_with_retry(
        self,
        *,
        experiment_paths: ExperimentPaths,
        variant_paths: VariantPaths,
        prompt_text: str,
        resources: ResourceFiles,
        validator: CorrectionValidator,
        reference_correction: Path | None = None,
    ) -> "GenerationResult":
        """Generate correction.yaml with up to MAX_CORRECTION_ATTEMPTS total attempts."""
        from .models import GenerationAttempt, GenerationResult
        from .exceptions import GenerationError
        from .correction_shape_validator import CorrectionShapeValidator

        self.prepare_workspace(experiment_paths=experiment_paths, variant_paths=variant_paths, prompt_text=prompt_text, resources=resources, reference_correction=reference_correction)
        variant_paths.correction_logs.mkdir(parents=True, exist_ok=True)
        generated = variant_paths.correction_workspace / "output" / "correction.yaml"
        last_result: CommandResult | None = None
        last_errors: tuple[str, ...] = ()
        attempts_log: list[GenerationAttempt] = []
        total_duration = 0.0

        for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
            if attempt == 1:
                instruction = self.adaptation_instruction() if reference_correction else self.instruction()
                # Remove file if not adaptation to force generation
                if not reference_correction and generated.exists():
                    generated.unlink()
            else:
                instruction = self.retry_instruction(last_errors)

            last_result = self._run_attempt(variant_paths=variant_paths, instruction=instruction, attempt=attempt)
            current_duration = last_result.duration_seconds
            current_code = last_result.return_code
            current_timeout = last_result.timed_out
            total_duration += current_duration

            if current_code != 0 or current_timeout:
                validation_errors = (f"{self.runner.provider} execution failed (return code {current_code}, timeout {current_timeout})",)
                valid = False
            elif not generated.is_file():
                validation_errors = (f"{self.runner.provider} completed without creating output/correction.yaml",)
                valid = False
            else:
                # Copy so validate() can read the final path.
                variant_paths.correction_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(generated, variant_paths.correction)
                validation = validator.validate(variant_paths.correction)

                if validation.valid and reference_correction:
                    shape_validation = CorrectionShapeValidator.validate(reference_correction, variant_paths.correction)
                    if not shape_validation.valid:
                        validation = shape_validation

                validation_errors = validation.errors
                valid = validation.valid

            attempts_log.append(GenerationAttempt(
                attempt=attempt,
                duration_seconds=current_duration,
                return_code=current_code,
                timed_out=current_timeout,
                success=valid,
                validation_errors=validation_errors
            ))

            if valid:
                return GenerationResult(
                    last_command_result=last_result,
                    calls=attempt,
                    retries=attempt - 1,
                    total_duration_seconds=total_duration,
                    attempts=tuple(attempts_log),
                    success=True
                )

            last_errors = validation_errors

        # All attempts exhausted without a valid correction.
        error_msg = f"Canonical correction still invalid after {MAX_CORRECTION_ATTEMPTS} attempt(s): " + "; ".join(last_errors)
        res = GenerationResult(
            last_command_result=last_result,
            calls=MAX_CORRECTION_ATTEMPTS,
            retries=MAX_CORRECTION_ATTEMPTS - 1,
            total_duration_seconds=total_duration,
            attempts=tuple(attempts_log),
            success=False
        )
        raise GenerationError(error_msg, res)
