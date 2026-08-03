from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, TextIO

from .config import PipelineConfig, load_config
from .exceptions import (
    ConfigurationError,
    PipelineError,
    PipelineJobError,
    PreflightError,
    PromptDiscoveryError,
    UnsafePathError,
)
from .lab_validator import LabValidator
from .models import JobStatus, PromptRecord, ValidationResult
from .pipeline import Pipeline, exit_code_for_summary
from .state_store import read_json
from .yaml_validator import YamlValidator


EXIT_SUCCESS = 0
EXIT_FAILED = 1
EXIT_ERROR = 2
EXIT_PREFLIGHT = 3


def _add_config_argument(parser: argparse.ArgumentParser, *, default: bool) -> None:
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("pipeline.yaml") if default else argparse.SUPPRESS,
        metavar="PATH",
        help="file di configurazione (default: pipeline.yaml)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kathara-pipeline",
        description="Genera e verifica sequenzialmente laboratori Kathara.",
    )
    _add_config_argument(parser, default=True)
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="esegue la pipeline")
    _add_config_argument(run_parser, default=False)
    selection = run_parser.add_mutually_exclusive_group(required=True)
    selection.add_argument(
        "--all",
        dest="all_prompts",
        action="store_true",
        help="elabora tutti i prompt scoperti",
    )
    selection.add_argument(
        "--prompt",
        metavar="FILENAME",
        help="elabora un solo prompt, selezionato per nome file",
    )
    run_parser.add_argument("--force", action="store_true", help="ignora gli skip idempotenti")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="mostra il piano senza creare file o avviare processi esterni",
    )

    for name, help_text in (
        ("status", "legge riepilogo e manifest esistenti"),
        ("validate", "valida localmente configurazione e artefatti esistenti"),
        ("preflight", "verifica tutti i prerequisiti, inclusi gli strumenti esterni"),
    ):
        command_parser = commands.add_parser(name, help=help_text)
        _add_config_argument(command_parser, default=False)

    return parser


def _job_directories(generated_root: Path) -> tuple[Path, ...]:
    if not generated_root.is_dir():
        return ()
    try:
        directories = (
            path
            for path in generated_root.iterdir()
            if path.is_dir() and not path.is_symlink() and not path.name.startswith(".")
        )
        return tuple(sorted(directories, key=lambda path: (path.name.casefold(), path.name)))
    except OSError as exc:
        raise PipelineJobError(
            f"Impossibile elencare gli artefatti in {generated_root}",
            details=(str(exc),),
        ) from exc


def _integer(value: Any) -> str:
    return str(value) if isinstance(value, int) and not isinstance(value, bool) else "?"


def _status_command(config: PipelineConfig, *, output: TextIO) -> int:
    """Render persisted state without discovering prompts or running preflight."""

    generated_root = config.paths.generated_labs
    found = False
    exit_code = EXIT_SUCCESS
    summary_path = generated_root / "pipeline-summary.json"
    summary = read_json(summary_path)
    if summary is not None:
        found = True
        counts = summary.get("counts")
        counts = counts if isinstance(counts, dict) else {}
        print("Riepilogo pipeline:", file=output)
        print(f"  Prompt trovati: {_integer(summary.get('prompts_found'))}", file=output)
        print(f"  Laboratori generati: {_integer(summary.get('labs_generated'))}", file=output)
        print(f"  Laboratori testati: {_integer(summary.get('labs_tested'))}", file=output)
        for status in ("passed", "failed", "error", "skipped"):
            print(f"  {status}: {_integer(counts.get(status))}", file=output)
        if isinstance(counts.get("error"), int) and counts["error"] > 0:
            exit_code = EXIT_ERROR
        elif isinstance(counts.get("failed"), int) and counts["failed"] > 0:
            exit_code = EXIT_FAILED

    manifests: list[dict[str, Any]] = []
    for job_dir in _job_directories(generated_root):
        manifest = read_json(job_dir / "manifest.json")
        if manifest is not None:
            manifests.append(manifest)
    if manifests:
        found = True
        print("Job:", file=output)
        for manifest in manifests:
            lab_id = manifest.get("lab_id")
            status = manifest.get("status")
            print(
                f"  {lab_id if isinstance(lab_id, str) else '?'}: "
                f"{status if isinstance(status, str) else 'unknown'}",
                file=output,
            )
            if status == JobStatus.ERROR.value:
                exit_code = EXIT_ERROR
            elif status == JobStatus.FAILED.value and exit_code == EXIT_SUCCESS:
                exit_code = EXIT_FAILED

    if not found:
        print("Nessuna esecuzione registrata.", file=output)
    return exit_code


def _prompt_text(job_dir: Path, prompts: dict[str, PromptRecord]) -> tuple[str, str | None]:
    copied_prompt = job_dir / "prompt.md"
    if copied_prompt.is_file():
        try:
            return copied_prompt.read_text(encoding="utf-8"), None
        except (OSError, UnicodeError) as exc:
            return "", f"{job_dir.name}: prompt.md non leggibile: {exc}"
    prompt = prompts.get(job_dir.name)
    if prompt is not None and prompt.content is not None:
        return prompt.content, None
    return "", None


def _print_validation(
    label: str,
    result: ValidationResult,
    *,
    output: TextIO,
) -> bool:
    if result.valid:
        print(f"  OK {label}", file=output)
        return True
    print(f"  ERRORE {label}", file=output)
    for error in result.errors:
        print(f"    - {error}", file=output)
    return False


def _validate_command(
    config: PipelineConfig,
    pipeline: Pipeline,
    *,
    output: TextIO,
) -> int:
    """Run only dry/local preflight and static validation of existing artifacts."""

    discovered = pipeline.discover()
    report = pipeline.preflight(discovered, dry_run=True)
    prompts_by_lab_id = {prompt.lab_id: prompt for prompt in discovered}
    lab_validator: LabValidator | None = None
    yaml_validator: YamlValidator | None = None
    valid = True
    artifact_count = 0

    for job_dir in _job_directories(config.paths.generated_labs):
        source = job_dir / "source"
        correction = job_dir / "correction" / "correction.yaml"
        if not source.exists() and not correction.exists():
            continue

        print(f"Validazione {job_dir.name}:", file=output)
        prompt_text, prompt_error = _prompt_text(job_dir, prompts_by_lab_id)
        if prompt_error:
            artifact_count += 1
            valid = False
            print(f"  ERRORE prompt: {prompt_error}", file=output)

        if source.exists():
            artifact_count += 1
            if lab_validator is None:
                lab_validator = LabValidator()
            valid = _print_validation(
                "source/",
                lab_validator.validate(source, prompt_text),
                output=output,
            ) and valid

        if correction.exists():
            artifact_count += 1
            if not source.is_dir():
                valid = False
                print("  ERRORE correction.yaml: source/ mancante o non valida", file=output)
            else:
                if yaml_validator is None:
                    yaml_validator = YamlValidator(
                        report.resources.schema_path,
                        report.resources.skill_path,
                    )
                valid = _print_validation(
                    "correction/correction.yaml",
                    yaml_validator.validate(correction, source, job_dir),
                    output=output,
                ) and valid

    if artifact_count == 0:
        print("Preflight locale completato; nessun artefatto esistente da validare.", file=output)
    elif valid:
        print(f"Validazione locale completata: {artifact_count} artefatti validi.", file=output)
    else:
        print("Validazione locale completata con errori.", file=output)
    return EXIT_SUCCESS if valid else EXIT_ERROR


def _preflight_command(
    pipeline: Pipeline,
    *,
    output: TextIO,
) -> int:
    prompts = pipeline.discover()
    pipeline.preflight(prompts, dry_run=False)
    print("Preflight completato con successo.", file=output)
    return EXIT_SUCCESS


def _emit_exception(exc: BaseException, *, output: TextIO) -> None:
    print(f"ERRORE: {exc}", file=output)
    for detail in getattr(exc, "details", ()):
        print(f"  - {detail}", file=output)


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "status":
            return _status_command(config, output=sys.stdout)

        pipeline = Pipeline(config)
        if args.command == "run":
            summary = pipeline.run(
                prompt_name=args.prompt,
                force=args.force,
                dry_run=args.dry_run,
            )
            return exit_code_for_summary(summary)
        if args.command == "validate":
            return _validate_command(config, pipeline, output=sys.stdout)
        if args.command == "preflight":
            return _preflight_command(pipeline, output=sys.stdout)
        raise AssertionError(f"Comando non gestito: {args.command}")
    except (ConfigurationError, PreflightError, PromptDiscoveryError, UnsafePathError) as exc:
        _emit_exception(exc, output=sys.stderr)
        return EXIT_PREFLIGHT
    except PipelineJobError as exc:
        _emit_exception(exc, output=sys.stderr)
        return EXIT_ERROR
    except PipelineError as exc:
        _emit_exception(exc, output=sys.stderr)
        return EXIT_PREFLIGHT
    except (OSError, UnicodeError, ValueError) as exc:
        _emit_exception(exc, output=sys.stderr)
        return EXIT_ERROR


__all__ = [
    "EXIT_ERROR",
    "EXIT_FAILED",
    "EXIT_PREFLIGHT",
    "EXIT_SUCCESS",
    "build_parser",
    "main",
]
