from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .correction_validator import CorrectionValidator
from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, VariantPaths, ResourceFiles

MAX_CORRECTION_ATTEMPTS = 2


class CorrectionGenerator:
    """Generate one candidate-independent correction for the paired experiment."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Read input/prompt.md, input/evaluation-spec.md, input/check-plan.md, candidate/ (the generated lab implementation), "
            "resources/checker/SKILL.md, and resources/checker/config-schema.md. "
            "Generate exactly one canonical output/correction.yaml for kathara-lab-checker. "
            "This is a per-variant correction: the correction MUST evaluate exactly the requirements frozen in "
            "input/evaluation-spec.md, using the evaluation strategy defined in input/check-plan.md. "
            "The candidate lab must ONLY provide the concrete values (device names, "
            "IP addresses, subnets, interfaces, next-hops, collision domains) needed to instantiate those requirements.\n\n"
            "CRITICAL REQUIREMENT-DRIVEN GENERATION:\n"
            "The evaluation strategy (which requirements are checked, which checker categories are used, and the strictness of those checks) "
            "is already determined and frozen inside check-plan.md. You MUST treat this strategy as mandatory. "
            "You must perform the exact same semantic checks and use the exact same checker categories as dictated by the check-plan.md, "
            "just as you would for any other candidate fulfilling the same specification. "
            "Do not add a check only because one candidate exposes more implementation details. "
            "Do not omit or weaken a check in one variant because its candidate is different. "
            "Examples:\n"
            "- if static routing is required with exact next-hop validation, use it for both variants;\n"
            "- if DNS resolution is required, both corrections must contain equivalent DNS checks;\n"
            "- if end-to-end reachability is required, both corrections must contain equivalent reachability checks.\n\n"
            "Automatically include every standard supported check that is explicitly specified or unambiguously derivable "
            "from the check-plan.md. Prefer standard checks over custom_commands unless explicitly required. "
            "IMPORTANT: lab_inline is mandatory and must contain the complete expected topology derived from the evaluation-spec "
            "and candidate lab. default_image is a mandatory checker field. "
            "Use lab_inline rather than structure and omit labs_path. Follow the runtime 0.1.14 compatibility rules in the Skill. "
            "Write only YAML to output/correction.yaml, with no surrounding prose. Do not create any other output file."
        )

    @staticmethod
    def adaptation_instruction() -> str:
        return (
            "Use the validated reference correction located in input/reference_correction.yaml as the evaluation template for this candidate. "
            "Read the current candidate/ lab and adapt only candidate-dependent concrete values required for the checks to apply to this laboratory. "
            "For example: device names, IP addresses, interface identifiers, gateways, next hops, route destinations, collision domains, lab_inline, router IDs, etc.\n\n"
            "Do not redesign the evaluation strategy. The semantic test plan is defined by input/evaluation-spec.md and input/check-plan.md. "
            "Preserve the same semantic checks and evaluation strictness. "
            "Do not copy candidate-specific values from the reference correction when they do not match the current candidate.\n\n"
            "Generate the adapted output/correction.yaml. Write only YAML with no surrounding prose. Do not create any other output file."
        )

    @staticmethod
    def retry_instruction(validation_errors: tuple[str, ...]) -> str:
        errors_text = "\n".join(f"  - {e}" for e in validation_errors)
        return (
            "The previously generated output/correction.yaml failed validation with the following errors:\n"
            f"{errors_text}\n\n"
            "Open the existing output/correction.yaml and correct in-place only the reported errors. "
            "Preserve all valid sections already present in the file. Do not regenerate the entire correction from scratch.\n"
            "Read input/prompt.md, input/evaluation-spec.md, input/check-plan.md, candidate/, resources/checker/SKILL.md, and resources/checker/config-schema.md again to guide your fixes. "
            "Evaluate exactly the requirements and follow the exact evaluation strategy frozen in input/check-plan.md, "
            "using concrete values from candidate/. "
            "CRITICAL: The evaluation strategy is frozen. Perform the exact same semantic checks and use the same checker categories as dictated by the specification. "
            "Do not add, omit, or weaken checks based on candidate-specific details. "
            "lab_inline is mandatory and must contain the complete expected topology (lab.conf format). It must be a non-empty string. "
            "Do not use structure. Do not include labs_path. "
            "Write only YAML to output/correction.yaml, with no surrounding prose. Do not create any other output file."
        )

    def prepare_workspace(self, *, experiment_paths: ExperimentPaths, variant_paths: VariantPaths, prompt_text: str, resources: ResourceFiles, reference_correction: Path | None = None) -> None:
        if variant_paths.correction_workspace.exists():
            shutil.rmtree(variant_paths.correction_workspace)
        (variant_paths.correction_workspace / "input").mkdir(parents=True)
        resource_dir = variant_paths.correction_workspace / "resources" / "checker"
        resource_dir.mkdir(parents=True)
        (variant_paths.correction_workspace / "output").mkdir()
        (variant_paths.correction_workspace / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")
        shutil.copy2(experiment_paths.evaluation_spec, variant_paths.correction_workspace / "input" / "evaluation-spec.md")
        shutil.copy2(experiment_paths.check_plan, variant_paths.correction_workspace / "input" / "check-plan.md")
        
        if reference_correction is not None:
            shutil.copy2(reference_correction, variant_paths.correction_workspace / "input" / "reference_correction.yaml")
        
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
        """Run one agent call and raise AgentExecutionError on hard failure."""
        generated = variant_paths.correction_workspace / "output" / "correction.yaml"
        # Only remove the file on the first attempt so retries can fix it in-place.
        if attempt == 1 and generated.exists():
            generated.unlink()
        result = self.runner.run(
            instruction=instruction,
            workspace=variant_paths.correction_workspace,
            output_last_message=variant_paths.correction_workspace / ".agent-last-message.txt",
            stdout_log=variant_paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.jsonl",
            stderr_log=variant_paths.correction_logs / f"{self.runner.provider}-correction-attempt{attempt}.stderr.log",
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
    ) -> CommandResult:
        """Generate correction.yaml with up to MAX_CORRECTION_ATTEMPTS total attempts.

        After each attempt the correction is validated; if invalid the agent is given the
        exact validation errors and asked to regenerate (same workspace, same inputs, candidate lab).
        On final failure an AgentExecutionError is raised.
        """
        self.prepare_workspace(experiment_paths=experiment_paths, variant_paths=variant_paths, prompt_text=prompt_text, resources=resources, reference_correction=reference_correction)
        variant_paths.correction_logs.mkdir(parents=True, exist_ok=True)
        generated = variant_paths.correction_workspace / "output" / "correction.yaml"
        last_result: CommandResult | None = None
        last_errors: tuple[str, ...] = ()

        for attempt in range(1, MAX_CORRECTION_ATTEMPTS + 1):
            if attempt == 1:
                instruction = self.adaptation_instruction() if reference_correction else self.instruction()
            else:
                instruction = self.retry_instruction(last_errors)
            last_result = self._run_attempt(variant_paths=variant_paths, instruction=instruction, attempt=attempt)
            # Copy so validate() can read the final path.
            variant_paths.correction_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(generated, variant_paths.correction)
            validation = validator.validate(variant_paths.correction)
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
