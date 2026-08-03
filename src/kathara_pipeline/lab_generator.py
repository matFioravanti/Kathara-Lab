from __future__ import annotations

import shutil
from pathlib import Path

from .codex_runner import CodexRunner, process_metadata_from_result
from .exceptions import LabGenerationError
from .models import CommandResult, JobPaths, PromptRecord
from .paths import safe_rmtree


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _validate_copy_source(root: Path) -> None:
    if not root.is_dir() or root.is_symlink():
        raise LabGenerationError(f"Generated output is not a regular directory: {root}")
    for path in root.rglob("*"):
        if path.is_symlink():
            if path.readlink().is_absolute():
                raise LabGenerationError(f"Absolute symlink is not permitted: {path}")
            if not _is_inside(path, root):
                raise LabGenerationError(f"Generated symlink escapes the workspace: {path}")


def _copy_tree_safely(source: Path, destination: Path) -> None:
    """Copy a validated tree without dereferencing symlinks."""

    _validate_copy_source(source)
    shutil.copytree(source, destination, symlinks=True)


def _unexpected_workspace_entries(workspace: Path, allowed_roots: tuple[Path, ...]) -> list[Path]:
    unexpected: list[Path] = []
    exact = {path.resolve() for path in allowed_roots if path.exists() and path.is_file()}
    directories = [path.resolve() for path in allowed_roots if path.exists() and path.is_dir()]
    structural_directories = {workspace.resolve()}
    for path in allowed_roots:
        parent = path if path.is_dir() else path.parent
        while _is_inside(parent, workspace):
            structural_directories.add(parent.resolve())
            if parent.resolve() == workspace.resolve():
                break
            parent = parent.parent
    for path in workspace.rglob("*"):
        resolved = path.resolve()
        if resolved in exact:
            continue
        if any(_is_inside(path, directory) for directory in directories):
            continue
        if path.is_dir() and not path.is_symlink() and resolved in structural_directories:
            continue
        unexpected.append(path)
    return unexpected


class LabGenerator:
    """Generate and collect one Kathara lab in an isolated Codex workspace."""

    def __init__(self, runner: CodexRunner, *, keep_workspace: bool = False) -> None:
        self.runner = runner
        self.keep_workspace = keep_workspace

    def generate(self, prompt: PromptRecord, job_paths: JobPaths) -> CommandResult:
        if prompt.content is None:
            raise LabGenerationError(
                f"Prompt {prompt.name} cannot be generated because it was not decoded"
            )

        workspace = job_paths.lab_workspace
        generated_root = job_paths.root.parent
        if workspace.exists() or workspace.is_symlink():
            safe_rmtree(workspace, generated_root)

        input_dir = workspace / "input"
        output_dir = workspace / "output"
        output_lab = output_dir / "lab"
        input_dir.mkdir(parents=True)
        output_lab.mkdir(parents=True)
        input_prompt = input_dir / "prompt.md"
        input_prompt.write_text(prompt.content, encoding="utf-8")
        final_message = workspace / ".codex-last-message.txt"

        instruction = self._instruction()
        try:
            result = self.runner.run(
                instruction=instruction,
                workspace=workspace,
                output_last_message=final_message,
                jsonl_log=job_paths.logs / "codex-lab.jsonl",
                stderr_log=job_paths.logs / "codex-lab.stderr.log",
            )
            metadata = process_metadata_from_result(
                result,
                cwd=workspace,
                jsonl_log=job_paths.logs / "codex-lab.jsonl",
                stderr_log=job_paths.logs / "codex-lab.stderr.log",
            )
            try:
                self._validate_workspace(
                    workspace=workspace,
                    input_prompt=input_prompt,
                    expected_prompt=prompt.content,
                    output_lab=output_lab,
                    final_message=final_message,
                )

                if job_paths.source.exists() or job_paths.source.is_symlink():
                    safe_rmtree(job_paths.source, generated_root)
                job_paths.source.parent.mkdir(parents=True, exist_ok=True)
                _copy_tree_safely(output_lab, job_paths.source)
            except LabGenerationError as exc:
                if exc.process_metadata is None:
                    exc.process_metadata = metadata
                raise
            except (OSError, UnicodeError, shutil.Error) as exc:
                raise LabGenerationError(
                    "Generated laboratory could not be validated or copied",
                    details=(str(exc),),
                    process_metadata=metadata,
                ) from exc
            return result
        finally:
            if not self.keep_workspace and (workspace.exists() or workspace.is_symlink()):
                safe_rmtree(workspace, generated_root)

    @staticmethod
    def _instruction() -> str:
        return (
            "Read only input/prompt.md. Generate exactly one complete Kathara laboratory "
            "inside output/lab/. Do not read other prompts or prior laboratories. Do not "
            "modify input/prompt.md and do not create files outside output/lab/. Do not "
            "generate correction.yaml and do not run Kathara or kathara_lab_checker. The "
            "laboratory must be complete, contain no placeholders, and be internally "
            "consistent across lab.conf, interfaces, startup files, routing, and services."
        )

    @staticmethod
    def _validate_workspace(
        *,
        workspace: Path,
        input_prompt: Path,
        expected_prompt: str,
        output_lab: Path,
        final_message: Path,
    ) -> None:
        try:
            actual_prompt = input_prompt.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise LabGenerationError("Codex removed or corrupted the immutable prompt input") from exc
        if actual_prompt != expected_prompt:
            raise LabGenerationError("Codex modified the immutable prompt input")
        if not output_lab.is_dir() or output_lab.is_symlink():
            raise LabGenerationError("Codex did not create output/lab as a directory")
        if not any(path.is_file() for path in output_lab.rglob("*")):
            raise LabGenerationError("Codex generated an empty laboratory")
        forbidden = [
            path
            for path in output_lab.rglob("*")
            if path.is_file() and path.name.casefold() == "correction.yaml"
        ]
        if forbidden:
            raise LabGenerationError("Codex generated correction.yaml during the lab phase")
        _validate_copy_source(output_lab)

        extras = _unexpected_workspace_entries(
            workspace,
            (input_prompt, output_lab, final_message),
        )
        if extras:
            relative = ", ".join(str(path.relative_to(workspace)) for path in extras)
            raise LabGenerationError(
                f"Codex wrote outside the authorized lab output directory: {relative}"
            )
