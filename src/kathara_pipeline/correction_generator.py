from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .correction_validator import CorrectionValidator
from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, ResourceFiles

MAX_CORRECTION_ATTEMPTS = 2


class CorrectionGenerator:
    """Generate one candidate-independent correction for the paired experiment."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Read input/prompt.md, input/evaluation-spec.md, resources/checker/SKILL.md, and resources/checker/config-schema.md. "
            "Generate exactly one canonical output/correction.yaml for kathara-lab-checker. "
            "This is a paired experiment: the correction MUST be derived exclusively from the prompt, the evaluation spec, and checker resources. "
            "No candidate laboratory is available and you must not assume implementation details not required by the prompt. "
            "The prompt is the authoritative source; if evaluation-spec.md introduces unjustified items, ignore them. "
            "Automatically include every standard supported check that is explicitly specified or unambiguously derivable. "
            "Prefer standard checks over custom_commands. Use custom_commands only as a deterministic fallback when the prompt "
            "explicitly requires a property that no standard check can represent. Never invent a check just to increase coverage. "
            "IMPORTANT: lab_inline is mandatory and must contain the complete expected topology derived exclusively from prompt.md. "
            "Use lab_inline rather than structure and omit labs_path. Follow the runtime 0.1.14 compatibility rules in the Skill. "
            "Write only YAML to output/correction.yaml, with no surrounding prose. Do not create any other output file."
        )

    @staticmethod
    def retry_instruction(validation_errors: tuple[str, ...]) -> str:
        errors_text = "\n".join(f"  - {e}" for e in validation_errors)
        return (
            "The previously generated output/correction.yaml failed validation with the following errors:\n"
            f"{errors_text}\n\n"
            "Read input/prompt.md, input/evaluation-spec.md, resources/checker/SKILL.md, and resources/checker/config-schema.md again and "
            "regenerate output/correction.yaml fixing all the errors above. "
            "The prompt is the authoritative source; if evaluation-spec.md introduces unjustified items, ignore them. "
            "CRITICAL: lab_inline is mandatory and must contain the complete expected topology (lab.conf format) "
            "derived exclusively from prompt.md. It must be a non-empty string. "
            "Do not use structure. Do not include labs_path. "
            "Write only YAML to output/correction.yaml, with no surrounding prose. Do not create any other output file."
        )

    def prepare_workspace(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> None:
        if paths.correction_workspace.exists():
            shutil.rmtree(paths.correction_workspace)
        (paths.correction_workspace / "input").mkdir(parents=True)
        resource_dir = paths.correction_workspace / "resources" / "checker"
        resource_dir.mkdir(parents=True)
        (paths.correction_workspace / "output").mkdir()
        (paths.correction_workspace / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")
        shutil.copy2(paths.evaluation_spec, paths.correction_workspace / "input" / "evaluation-spec.md")
        shutil.copy2(resources.checker_skill, resource_dir / "SKILL.md")
        shutil.copy2(resources.checker_schema, resource_dir / "config-schema.md")

    def _run_attempt(
        self,
        *,
        paths: ExperimentPaths,
        instruction: str,
        attempt: int,
    ) -> CommandResult:
        """Run one agent call and raise AgentExecutionError on hard failure."""
        # Remove any previously generated correction to avoid stale files being reused.
        generated = paths.correction_workspace / "output" / "correction.yaml"
        if generated.exists():
            generated.unlink()
        result = self.runner.run(
            instruction=instruction,
            workspace=paths.correction_workspace,
            output_last_message=paths.correction_workspace / ".agent-last-message.txt",
            stdout_log=paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.jsonl",
            stderr_log=paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )
        if result.return_code != 0 or result.timed_out:
            raise AgentExecutionError(
                f"{self.runner.provider} correction generation failed (return code {result.return_code}, attempt {attempt})"
            )
        if not generated.is_file():
            raise AgentExecutionError(
                f"{self.runner.provider} completed without creating output/correction.yaml (attempt {attempt})"
            )
        return result

    def generate(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> CommandResult:
        """Single-attempt generation (kept for backward compatibility)."""
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, resources=resources)
        paths.correction_logs.mkdir(parents=True, exist_ok=True)
        result = self._run_attempt(paths=paths, instruction=self.instruction(), attempt=1)
        paths.correction_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paths.correction_workspace / "output" / "correction.yaml", paths.correction)
        return result

    def generate_with_retry(
        self,
        *,
        paths: ExperimentPaths,
        prompt_text: str,
        resources: ResourceFiles,
        validator: CorrectionValidator,
    ) -> CommandResult:
        """Generate correction.yaml with up to MAX_CORRECTION_ATTEMPTS total attempts.

        After each attempt the correction is validated; if invalid the agent is given the
        exact validation errors and asked to regenerate (same workspace, same inputs, no
        candidate lab source ever exposed). On final failure an AgentExecutionError is raised.
        """
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, resources=resources)
        paths.correction_logs.mkdir(parents=True, exist_ok=True)
        generated = paths.correction_workspace / "output" / "correction.yaml"
        last_result: CommandResult | None = None
        last_errors: tuple[str, ...] = ()

        for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
            instruction = self.instruction() if attempt == 1 else self.retry_instruction(last_errors)
            last_result = self._run_attempt(paths=paths, instruction=instruction, attempt=attempt)
            # Copy so validate() can read the final path.
            paths.correction_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(generated, paths.correction)
            validation = validator.validate(paths.correction)
            if validation.valid:
                return last_result
            last_errors = validation.errors
            if attempt < MAX_CORRECTION_ATTEMPTS:
                # Leave workspace intact so the agent retries with the same inputs.
                continue

        # All attempts exhausted without a valid correction.
        raise AgentExecutionError(
            f"Canonical correction still invalid after {MAX_CORRECTION_ATTEMPTS} attempt(s): "
            + "; ".join(last_errors)
        )
