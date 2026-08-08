from __future__ import annotations

import shutil
from pathlib import Path

from .agent_runner import AgentRunner
from .exceptions import AgentExecutionError
from .models import CommandResult, ResourceFiles, Variant, VariantPaths


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

    def generate(
        self,
        *,
        paths: VariantPaths,
        prompt_text: str,
        variant: Variant,
        resources: ResourceFiles,
    ) -> CommandResult:
        self.prepare_workspace(paths=paths, prompt_text=prompt_text, variant=variant, resources=resources)
        paths.logs.mkdir(parents=True, exist_ok=True)
        result = self.runner.run(
            instruction=self.instruction(variant),
            workspace=paths.workspace,
            output_last_message=paths.workspace / ".agent-last-message.txt",
            stdout_log=paths.logs / f"{self.runner.provider}-lab.jsonl",
            stderr_log=paths.logs / f"{self.runner.provider}-lab.stderr.log",
            timeout_seconds=self.timeout_seconds,
        )
        if result.return_code != 0 or result.timed_out:
            raise AgentExecutionError(
                f"{self.runner.provider} lab generation failed (return code {result.return_code})"
            )
        generated = paths.workspace / "output" / "lab"
        if not generated.is_dir():
            raise AgentExecutionError(
                f"{self.runner.provider} completed without creating output/lab/"
            )
        if paths.source.exists():
            shutil.rmtree(paths.source)
        shutil.copytree(generated, paths.source, symlinks=True)
        return result
