from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, ResourceFiles


class EvaluationPlanGenerator:
    """Generate both evaluation-spec.md and check-plan.md from prompt and Creation Skill in a single invocation."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Read input/prompt.md and resources/creation/SKILL.md. "
            "Also read resources/checker/SKILL.md and resources/checker/config-schema.md. "
            "You must generate EXACTLY TWO files in the output/ directory: output/evaluation-spec.md and output/check-plan.md.\n\n"
            "1. output/evaluation-spec.md:\n"
            "This file must structure the explicit requirements found in the prompt using the Creation Skill as a guide. "
            "CRITICAL: It must describe ONLY WHAT the scenario requires. It must contain ONLY candidate-independent scenario requirements. "
            "It must NOT mention checker blocks, strategies, or validation strictness. "
            "It must NOT contain any candidate-specific values if they are missing from the prompt.\n\n"
            "2. output/check-plan.md:\n"
            "This file must freeze the evaluation strategy for every requirement listed in evaluation-spec.md. "
            "CRITICAL: For every requirement, you MUST specify:\n"
            "- Which checker category/block represents it.\n"
            "- The validation strictness.\n"
            "- Which concrete values must later be resolved from the candidate lab.\n"
            "This strategy MUST be completely candidate-independent. "
            "A missing concrete value must NOT cause the requirement to be omitted. "
            "Only mark a requirement as not checkable when kathara-lab-checker genuinely has no supported way to represent it.\n\n"
            "Do NOT write anything outside these two files."
        )

    def prepare_workspace(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> None:
        if paths.evaluation_plan_workspace.exists():
            shutil.rmtree(paths.evaluation_plan_workspace)
        (paths.evaluation_plan_workspace / "input").mkdir(parents=True)
        (paths.evaluation_plan_workspace / "output").mkdir(parents=True)
        
        creation_dir = paths.evaluation_plan_workspace / "resources" / "creation"
        creation_dir.mkdir(parents=True)
        checker_dir = paths.evaluation_plan_workspace / "resources" / "checker"
        checker_dir.mkdir(parents=True)
        
        (paths.evaluation_plan_workspace / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")
        shutil.copy2(resources.creation_skill, creation_dir / "SKILL.md")
        shutil.copy2(resources.checker_skill, checker_dir / "SKILL.md")
        shutil.copy2(resources.checker_schema, checker_dir / "config-schema.md")

    def generate(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> CommandResult:
        """Run agent to generate both evaluation-spec.md and check-plan.md."""
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, resources=resources)
        paths.evaluation_plan_logs.mkdir(parents=True, exist_ok=True)
        
        spec_generated = paths.evaluation_plan_workspace / "output" / "evaluation-spec.md"
        plan_generated = paths.evaluation_plan_workspace / "output" / "check-plan.md"
        
        result = self.runner.run(
            instruction=self.instruction(),
            workspace=paths.evaluation_plan_workspace,
            output_last_message=paths.evaluation_plan_workspace / ".agent-last-message.txt",
            stdout_log=paths.evaluation_plan_logs / f"{self.runner.provider}-evaluation-plan.jsonl",
            stderr_log=paths.evaluation_plan_logs / f"{self.runner.provider}-evaluation-plan.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )
        if result.return_code != 0 or result.timed_out:
            raise AgentExecutionError(
                f"{self.runner.provider} evaluation plan generation failed (return code {result.return_code})"
            )
        
        missing = []
        if not spec_generated.is_file():
            missing.append("evaluation-spec.md")
        if not plan_generated.is_file():
            missing.append("check-plan.md")
            
        if missing:
            raise AgentExecutionError(
                f"{self.runner.provider} completed without creating: {', '.join(missing)}"
            )
        
        # Copy to the root experiment folder
        shutil.copy2(spec_generated, paths.evaluation_spec)
        shutil.copy2(plan_generated, paths.check_plan)
        return result
