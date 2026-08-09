from __future__ import annotations

import shutil

from .agent_runner import AgentRunner
from .exceptions import AgentExecutionError
from .models import CommandResult, ExperimentPaths, ResourceFiles


class EvaluationSpecGenerator:
    """Generate evaluation-spec.md from prompt and Creation Skill."""

    def __init__(self, runner: AgentRunner, timeout_seconds: int):
        self.runner = runner
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def instruction() -> str:
        return (
            "Read input/prompt.md and resources/creation/SKILL.md. "
            "Generate exactly one file output/evaluation-spec.md. "
            "This file must structure the explicit requirements found in the prompt using the Creation Skill as a guide. "
            "CRITICAL: The evaluation-spec.md must describe ONLY WHAT the scenario requires. "
            "It must contain ONLY candidate-independent scenario requirements. "
            "It must NOT mention checker blocks (such as kernel_routes, reachability, etc.), strategies, or validation strictness. "
            "It must NOT contain any candidate-specific values (e.g. concrete IPs, device names, prefixes, interfaces) if they are missing from the prompt. "
            "Do NOT decide whether a checker assertion is omitted or not checkable. "
            "Do NOT add reasonable defaults, and do NOT invent any IP addresses, routing protocols, "
            "services, topologies, or other requirements that are not explicitly present in the prompt. "
            "This file is strictly for extracting and freezing the scenario requirements. "
            "Write only markdown content."
        )

    def prepare_workspace(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> None:
        if paths.evaluation_spec_workspace.exists():
            shutil.rmtree(paths.evaluation_spec_workspace)
        (paths.evaluation_spec_workspace / "input").mkdir(parents=True)
        resource_dir = paths.evaluation_spec_workspace / "resources" / "creation"
        resource_dir.mkdir(parents=True)
        (paths.evaluation_spec_workspace / "output").mkdir()
        (paths.evaluation_spec_workspace / "input" / "prompt.md").write_text(prompt_text, encoding="utf-8")
        shutil.copy2(resources.creation_skill, resource_dir / "SKILL.md")

    def generate(self, *, paths: ExperimentPaths, prompt_text: str, resources: ResourceFiles) -> CommandResult:
        """Run agent to generate evaluation-spec.md."""
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, resources=resources)
        paths.evaluation_spec_logs.mkdir(parents=True, exist_ok=True)
        
        generated = paths.evaluation_spec_workspace / "output" / "evaluation-spec.md"
        result = self.runner.run(
            instruction=self.instruction(),
            workspace=paths.evaluation_spec_workspace,
            output_last_message=paths.evaluation_spec_workspace / ".agent-last-message.txt",
            stdout_log=paths.evaluation_spec_logs / f"{self.runner.provider}-evaluation-spec.jsonl",
            stderr_log=paths.evaluation_spec_logs / f"{self.runner.provider}-evaluation-spec.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )
        if result.return_code != 0 or result.timed_out:
            raise AgentExecutionError(
                f"{self.runner.provider} evaluation-spec generation failed (return code {result.return_code})"
            )
        if not generated.is_file():
            raise AgentExecutionError(
                f"{self.runner.provider} completed without creating output/evaluation-spec.md"
            )
        
        # Copy to the root experiment folder without extra directories
        shutil.copy2(generated, paths.evaluation_spec)
        return result
