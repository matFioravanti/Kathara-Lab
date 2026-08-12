from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner

from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, PairedGenerationResult, VariantPaths, ResourceFiles

MAX_CORRECTION_ATTEMPTS = 2


class CorrectionGenerator:
    """Generate correction.yaml files for the paired experiment."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Read input/prompt.md to understand what must be tested.\n"
            "Read candidate/ (the generated lab implementation) to resolve the concrete values "
            "needed to instantiate those tests: device names, IP addresses, interfaces, "
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
    def paired_instruction() -> str:
        return (
            "Read input/prompt.md to understand what must be tested.\n\n"
            "Two candidate laboratories are provided:\n"
            "  - candidates/with_skill/   (lab generated with the Kathara creation skill)\n"
            "  - candidates/without_skill/ (lab generated without the skill)\n\n"
            "Read resources/checker/SKILL.md and resources/checker/config-schema.md.\n\n"
            "For EACH candidate, independently read its lab files and produce a separate correction:\n"
            "  - output/with_skill/correction.yaml   (based on candidates/with_skill/)\n"
            "  - output/without_skill/correction.yaml (based on candidates/without_skill/)\n\n"
            "Both corrections must verify the same requirements described in input/prompt.md, "
            "but must be built separately from the concrete implementation of each lab.\n\n"
            "IMPORTANT: Do NOT copy IP addresses, routes, interfaces, gateways, device names, "
            "collision domains, or any other concrete values from one lab to the other. "
            "Each correction must reflect only its own candidate lab.\n\n"
            "For each correction: lab_inline is mandatory and must contain the complete expected "
            "topology derived from that candidate lab. default_image is a mandatory checker field. "
            "Use lab_inline rather than structure and omit labs_path. "
            "Follow the runtime 0.1.14 compatibility rules in the Skill.\n\n"
            "Write only YAML to each output file, with no surrounding prose. "
            "Do not create any other output files."
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

    # ------------------------------------------------------------------ #
    # Workspace preparation                                                #
    # ------------------------------------------------------------------ #

    def prepare_workspace(
        self,
        *,
        experiment_paths: ExperimentPaths,
        variant_paths: VariantPaths,
        prompt_text: str,
        resources: ResourceFiles,

    ) -> None:
        if variant_paths.correction_workspace.exists():
            shutil.rmtree(variant_paths.correction_workspace)
        (variant_paths.correction_workspace / "input").mkdir(parents=True)
        resource_dir = variant_paths.correction_workspace / "resources" / "checker"
        resource_dir.mkdir(parents=True)
        (variant_paths.correction_workspace / "output").mkdir()

        # Write the original prompt so the agent can read what must be tested
        (variant_paths.correction_workspace / "input" / "prompt.md").write_text(
            prompt_text, encoding="utf-8"
        )


        shutil.copytree(variant_paths.source, variant_paths.correction_workspace / "candidate")

        shutil.copy2(resources.checker_skill, resource_dir / "SKILL.md")
        shutil.copy2(resources.checker_schema, resource_dir / "config-schema.md")

    def prepare_paired_workspace(
        self,
        *,
        experiment_paths: ExperimentPaths,
        with_skill_paths: VariantPaths,
        without_skill_paths: VariantPaths,
        prompt_text: str,
        resources: ResourceFiles,
    ) -> Path:
        """Prepare a single shared workspace for paired generation.

        Returns the paired workspace path.
        """
        paired_ws = experiment_paths.root / ".workspaces" / "correction_paired"
        if paired_ws.exists():
            shutil.rmtree(paired_ws)

        (paired_ws / "input").mkdir(parents=True)
        resource_dir = paired_ws / "resources" / "checker"
        resource_dir.mkdir(parents=True)
        (paired_ws / "output" / "with_skill").mkdir(parents=True)
        (paired_ws / "output" / "without_skill").mkdir(parents=True)
        (paired_ws / "logs").mkdir(parents=True)

        # Write the original prompt so the agent can read what must be tested
        (paired_ws / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")

        shutil.copytree(with_skill_paths.source, paired_ws / "candidates" / "with_skill")
        shutil.copytree(without_skill_paths.source, paired_ws / "candidates" / "without_skill")

        shutil.copy2(resources.checker_skill, resource_dir / "SKILL.md")
        shutil.copy2(resources.checker_schema, resource_dir / "config-schema.md")

        return paired_ws

    # ------------------------------------------------------------------ #
    # Internal runner helpers                                              #
    # ------------------------------------------------------------------ #

    def _run_attempt(
        self,
        *,
        variant_paths: VariantPaths,
        instruction: str,
        attempt: int,
    ) -> CommandResult:
        """Run one agent call for standalone generation."""
        return self.runner.run(
            instruction=instruction,
            workspace=variant_paths.correction_workspace,
            output_last_message=variant_paths.correction_workspace / ".agent-last-message.txt",
            stdout_log=variant_paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.jsonl",
            stderr_log=variant_paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def generate(self, *, experiment_paths: ExperimentPaths, variant_paths: VariantPaths, prompt_text: str, resources: ResourceFiles) -> CommandResult:
        """Single-attempt generation (kept for backward compatibility)."""
        self.prepare_workspace(experiment_paths=experiment_paths, variant_paths=variant_paths, prompt_text=prompt_text, resources=resources)
        variant_paths.correction_logs.mkdir(parents=True, exist_ok=True)
        result = self._run_attempt(variant_paths=variant_paths, instruction=self.instruction(), attempt=1)
        variant_paths.correction_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(variant_paths.correction_workspace / "output" / "correction.yaml", variant_paths.correction)
        return result

    def generate_pair(
        self,
        *,
        experiment_paths: ExperimentPaths,
        with_skill_paths: VariantPaths,
        without_skill_paths: VariantPaths,
        prompt_text: str,
        resources: ResourceFiles,
    ) -> PairedGenerationResult:
        """Generate both corrections with a single agent call.

        Prepares one shared workspace, runs the agent once, then validates each
        correction separately. No retry is performed — the caller decides what to
        do when one or both corrections are invalid.
        """
        paired_ws = self.prepare_paired_workspace(
            experiment_paths=experiment_paths,
            with_skill_paths=with_skill_paths,
            without_skill_paths=without_skill_paths,
            prompt_text=prompt_text,
            resources=resources,
        )

        logs_dir = paired_ws / "logs"
        result = self.runner.run(
            instruction=self.paired_instruction(),
            workspace=paired_ws,
            output_last_message=paired_ws / ".agent-last-message.txt",
            stdout_log=logs_dir / f"{self.runner.provider}-paired-correction-attempt1.jsonl",
            stderr_log=logs_dir / f"{self.runner.provider}-paired-correction-attempt1.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )

        def _validate_and_copy(
            output_subdir: str,
            target_paths: VariantPaths,
        ) -> tuple[bool, tuple[str, ...]]:
            if result.return_code != 0 or result.timed_out:
                return False, (
                    f"{self.runner.provider} execution failed "
                    f"(return code {result.return_code}, timeout {result.timed_out})",
                )
            generated = paired_ws / "output" / output_subdir / "correction.yaml"
            if not generated.is_file():
                return False, (
                    f"{self.runner.provider} completed without creating "
                    f"output/{output_subdir}/correction.yaml",
                )
            target_paths.correction_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(generated, target_paths.correction)
            return True, ()

        ws_valid, ws_errors = _validate_and_copy("with_skill", with_skill_paths)
        wo_valid, wo_errors = _validate_and_copy("without_skill", without_skill_paths)

        return PairedGenerationResult(
            last_command_result=result,
            duration_seconds=result.duration_seconds,
            with_skill_valid=ws_valid,
            without_skill_valid=wo_valid,
            with_skill_errors=ws_errors,
            without_skill_errors=wo_errors,
        )

    def generate_with_retry(
        self,
        *,
        experiment_paths: ExperimentPaths,
        variant_paths: VariantPaths,
        prompt_text: str,
        resources: ResourceFiles,

    ) -> "GenerationResult":
        """Generate correction.yaml with up to MAX_CORRECTION_ATTEMPTS total attempts."""
        from .models import GenerationAttempt, GenerationResult
        from .exceptions import GenerationError

        self.prepare_workspace(experiment_paths=experiment_paths, variant_paths=variant_paths, prompt_text=prompt_text, resources=resources)
        variant_paths.correction_logs.mkdir(parents=True, exist_ok=True)
        generated = variant_paths.correction_workspace / "output" / "correction.yaml"
        last_result: CommandResult | None = None
        last_errors: tuple[str, ...] = ()
        attempts_log: list[GenerationAttempt] = []
        total_duration = 0.0

        for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
            if attempt == 1:
                instruction = self.instruction()
                if generated.exists():
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
                variant_paths.correction_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(generated, variant_paths.correction)
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
