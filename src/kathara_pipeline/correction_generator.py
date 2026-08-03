from __future__ import annotations

import shutil
from pathlib import Path

from .codex_runner import CodexRunner, process_metadata_from_result
from .exceptions import CorrectionGenerationError, LabGenerationError
from .lab_generator import _copy_tree_safely, _is_inside, _unexpected_workspace_entries
from .models import CommandResult, JobPaths, PromptRecord, ResourceFiles
from .paths import safe_rmtree
from .state_store import hash_directory


def _tree_shape(root: Path) -> tuple[tuple[str, str, str | None], ...]:
    entries: list[tuple[str, str, str | None]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries.append((relative, "symlink", str(path.readlink())))
        elif path.is_dir():
            entries.append((relative, "directory", None))
        elif path.is_file():
            entries.append((relative, "file", None))
        else:
            entries.append((relative, "other", None))
    return tuple(entries)


def _tree_snapshot(root: Path) -> tuple[dict[str, str], tuple[tuple[str, str, str | None], ...]]:
    return hash_directory(root), _tree_shape(root)


class CorrectionGenerator:
    """Generate exactly one correction YAML in a second isolated workspace."""

    def __init__(self, runner: CodexRunner, *, keep_workspace: bool = False) -> None:
        self.runner = runner
        self.keep_workspace = keep_workspace

    def generate(
        self,
        prompt: PromptRecord,
        job_paths: JobPaths,
        resources: ResourceFiles,
    ) -> CommandResult:
        if prompt.content is None:
            raise CorrectionGenerationError(
                f"Prompt {prompt.name} cannot be used because it was not decoded"
            )
        if not job_paths.source.is_dir() or job_paths.source.is_symlink():
            raise CorrectionGenerationError("Validated source laboratory is missing")

        workspace = job_paths.correction_workspace
        generated_root = job_paths.root.parent
        if workspace.exists() or workspace.is_symlink():
            safe_rmtree(workspace, generated_root)

        input_dir = workspace / "input"
        input_lab = input_dir / "lab"
        resources_dir = workspace / "resources"
        output_dir = workspace / "output"
        input_dir.mkdir(parents=True)
        resources_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)

        try:
            skill_copy, schema_copy, examples_copy = self._populate_workspace(
                prompt_content=prompt.content,
                source_lab=job_paths.source,
                input_prompt=input_dir / "prompt.md",
                input_lab=input_lab,
                resources=resources,
                resources_dir=resources_dir,
            )
            immutable_before = _tree_snapshot(input_dir), _tree_snapshot(resources_dir)
        except Exception:
            if not self.keep_workspace and (workspace.exists() or workspace.is_symlink()):
                safe_rmtree(workspace, generated_root)
            raise
        correction_output = output_dir / "correction.yaml"
        final_message = workspace / ".codex-last-message.txt"
        instruction = self._instruction(
            skill_name=skill_copy.name,
            schema_name=schema_copy.name,
            has_examples=examples_copy is not None,
        )
        try:
            result = self.runner.run(
                instruction=instruction,
                workspace=workspace,
                output_last_message=final_message,
                jsonl_log=job_paths.logs / "codex-correction.jsonl",
                stderr_log=job_paths.logs / "codex-correction.stderr.log",
            )
            metadata = process_metadata_from_result(
                result,
                cwd=workspace,
                jsonl_log=job_paths.logs / "codex-correction.jsonl",
                stderr_log=job_paths.logs / "codex-correction.stderr.log",
            )
            try:
                immutable_after = _tree_snapshot(workspace / "input"), _tree_snapshot(resources_dir)
                if immutable_after != immutable_before:
                    raise CorrectionGenerationError(
                        "Codex modified immutable correction inputs or resources"
                    )
                self._validate_workspace(
                    workspace=workspace,
                    input_dir=input_dir,
                    resources_dir=resources_dir,
                    correction_output=correction_output,
                    final_message=final_message,
                )

                destination = job_paths.correction
                if not _is_inside(destination, job_paths.root):
                    raise CorrectionGenerationError("Correction destination escapes the job directory")
                if destination.is_symlink() or destination.is_dir():
                    raise CorrectionGenerationError(
                        f"Unsafe correction destination already exists: {destination}"
                    )
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(correction_output, destination)
            except CorrectionGenerationError as exc:
                if exc.process_metadata is None:
                    exc.process_metadata = metadata
                raise
            except (OSError, UnicodeError, shutil.Error) as exc:
                raise CorrectionGenerationError(
                    "Generated correction file could not be validated or copied",
                    details=(str(exc),),
                    process_metadata=metadata,
                ) from exc
            return result
        finally:
            if not self.keep_workspace and (workspace.exists() or workspace.is_symlink()):
                safe_rmtree(workspace, generated_root)

    @staticmethod
    def _copy_regular_resource(source: Path, destination: Path) -> None:
        if not source.is_file() or source.is_symlink():
            raise CorrectionGenerationError(f"Resource is not a regular file: {source}")
        shutil.copy2(source, destination)

    def _populate_workspace(
        self,
        *,
        prompt_content: str,
        source_lab: Path,
        input_prompt: Path,
        input_lab: Path,
        resources: ResourceFiles,
        resources_dir: Path,
    ) -> tuple[Path, Path, Path | None]:
        input_prompt.write_text(prompt_content, encoding="utf-8")
        try:
            _copy_tree_safely(source_lab, input_lab)
        except LabGenerationError as exc:
            raise CorrectionGenerationError(
                "The source laboratory cannot be copied safely into the correction workspace",
                details=(str(exc),),
            ) from exc

        skill_copy = resources_dir / resources.skill_path.name
        schema_copy = resources_dir / resources.schema_path.name
        self._copy_regular_resource(resources.skill_path, skill_copy)
        self._copy_regular_resource(resources.schema_path, schema_copy)
        examples_copy: Path | None = None
        if resources.examples_path is not None:
            examples_copy = resources_dir / "examples"
            try:
                _copy_tree_safely(resources.examples_path, examples_copy)
            except LabGenerationError as exc:
                raise CorrectionGenerationError(
                    "Checker examples cannot be copied safely",
                    details=(str(exc),),
                ) from exc
        return skill_copy, schema_copy, examples_copy

    @staticmethod
    def _instruction(*, skill_name: str, schema_name: str, has_examples: bool) -> str:
        examples = (
            "Read resources/examples/ only as reference; never copy an example literally. "
            if has_examples
            else ""
        )
        return (
            "Read input/prompt.md, the complete input/lab/, resources/"
            f"{skill_name}, and resources/{schema_name}. {examples}"
            "Generate only output/correction.yaml. The file body must contain no comments, "
            "explanations, or surrounding prose. Follow only checks supported by the supplied "
            "Skill and schema. Apply the checker 0.1.14 syntax verified locally where the "
            "Markdown examples conflict with the installed implementation: HTTP uses "
            "status_code; OSPF neighbors use router_id/state, routes use objects with route, "
            "and interface keys use ethN; EVPN uses protocols.bgpd.evpn_sessions and "
            "protocols.bgpd.vtep_devices. A one-path kernel route must identify either its "
            "gateway or its ethN interface, not both. Prefer "
            "lab_inline so the correction does not depend on an absolute path. Reflect the "
            "laboratory's actual implementation without omitting prompt requirements. Do not "
            "modify input/ or resources/, do not modify the source laboratory, do not run the "
            "checker, and do not create any other file."
        )

    @staticmethod
    def _validate_workspace(
        *,
        workspace: Path,
        input_dir: Path,
        resources_dir: Path,
        correction_output: Path,
        final_message: Path,
    ) -> None:
        if not correction_output.is_file() or correction_output.is_symlink():
            raise CorrectionGenerationError(
                "Codex did not create a regular output/correction.yaml file"
            )
        if not correction_output.read_text(encoding="utf-8").strip():
            raise CorrectionGenerationError("Codex generated an empty correction.yaml")
        extras = _unexpected_workspace_entries(
            workspace,
            (input_dir, resources_dir, correction_output, final_message),
        )
        if extras:
            relative = ", ".join(str(path.relative_to(workspace)) for path in extras)
            raise CorrectionGenerationError(
                f"Codex wrote outside output/correction.yaml: {relative}"
            )
