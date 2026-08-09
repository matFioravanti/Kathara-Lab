from __future__ import annotations

import shutil

from .agent_runner import AgentRunner
from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, ResourceFiles


class CheckPlanGenerator:
    """Generate check-plan.md to define the evaluation strategy based on the prompt and evaluation-spec.md."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Read input/prompt.md and input/evaluation-spec.md. "
            "Also read resources/checker/SKILL.md and resources/checker/config-schema.md. "
            "Generate exactly one file output/check-plan.md. "
            "This file must freeze, for every requirement listed in evaluation-spec.md, the evaluation strategy. "
            "CRITICAL: For every requirement, you MUST specify:\n"
            "- Which checker category/block represents it (e.g., 'kernel_routes', 'reachability').\n"
            "- The validation strictness (e.g., 'exact next-hop', 'exact matching').\n"
            "- Which concrete values must later be resolved from the candidate lab (e.g., 'client device name', 'server IP').\n\n"
            "This strategy MUST be completely candidate-independent. It will be shared across all candidate evaluations. "
            "A missing concrete value (IPs, device names, prefixes, etc.) in the original prompt must NOT cause the requirement to be omitted. "
            "Only mark a requirement as not checkable when kathara-lab-checker genuinely has no supported way to represent that requirement. "
            "Write only markdown content."
        )

    def prepare_workspace(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> None:
        if paths.check_plan_workspace.exists():
            shutil.rmtree(paths.check_plan_workspace)
        (paths.check_plan_workspace / "input").mkdir(parents=True)
        checker_dir = paths.check_plan_workspace / "resources" / "checker"
        checker_dir.mkdir(parents=True)
        (paths.check_plan_workspace / "output").mkdir()
        (paths.check_plan_workspace / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")
        shutil.copy2(paths.evaluation_spec, paths.check_plan_workspace / "input" / "evaluation-spec.md")
        shutil.copy2(resources.checker_skill, checker_dir / "SKILL.md")
        shutil.copy2(resources.checker_schema, checker_dir / "config-schema.md")

    def generate(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> CommandResult:
        """Run agent to generate check-plan.md."""
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, resources=resources)
        paths.check_plan_logs.mkdir(parents=True, exist_ok=True)
        
        generated = paths.check_plan_workspace / "output" / "check-plan.md"
        result = self.runner.run(
            instruction=self.instruction(),
            workspace=paths.check_plan_workspace,
            output_last_message=paths.check_plan_workspace / ".agent-last-message.txt",
            stdout_log=paths.check_plan_logs / f"{self.runner.provider}-check-plan.jsonl",
            stderr_log=paths.check_plan_logs / f"{self.runner.provider}-check-plan.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )
        if result.return_code != 0 or result.timed_out:
            raise AgentExecutionError(
                f"{self.runner.provider} check-plan generation failed (return code {result.return_code})"
            )
        if not generated.is_file():
            raise AgentExecutionError(
                f"{self.runner.provider} completed without creating output/check-plan.md"
            )
        
        # Copy to the root experiment folder
        shutil.copy2(generated, paths.check_plan)
        return result
