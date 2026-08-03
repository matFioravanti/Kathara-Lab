from __future__ import annotations

import importlib.metadata
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .config import PipelineConfig
from .exceptions import PreflightError, UnsafePathError
from .models import PromptRecord, ResourceFiles
from .paths import detect_lab_id_collisions, ensure_generated_root_managed, paths_overlap
from .resource_discovery import discover_resources
from .yaml_validator import schema_support_errors


@dataclass(frozen=True, slots=True)
class PreflightReport:
    resources: ResourceFiles
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors

    def require_ok(self) -> None:
        if self.errors:
            raise PreflightError("Preflight non superato.", self.errors)


def _run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _checker_documents_yaml(_resources: ResourceFiles) -> bool:
    try:
        distribution = importlib.metadata.distribution("kathara-lab-checker")
        metadata = distribution.read_text("METADATA") or ""
    except (importlib.metadata.PackageNotFoundError, OSError, UnicodeError):
        metadata = ""
    evidence = metadata.casefold()
    if "yaml" in evidence and "lab_inline" in evidence:
        return True
    try:
        spec = importlib.util.find_spec("kathara_lab_checker")
        if spec is None or spec.origin is None:
            return False
        package_root = Path(spec.origin).resolve().parent
        source = (package_root / "__main__.py").read_text(encoding="utf-8").casefold()
    except (OSError, UnicodeError, ImportError, AttributeError):
        return False
    return "yaml.safe_load" in source and "lab_inline" in source


def _validate_collisions(prompts: list[PromptRecord]) -> list[str]:
    return [
        f"Collisione lab-id '{lab_id}': {', '.join(path.name for path in paths)}"
        for lab_id, paths in detect_lab_id_collisions(prompts).items()
    ]


def _nearest_existing_directory(path: Path) -> Path | None:
    candidate = path
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate if candidate.is_dir() else None


def run_preflight(
    config: PipelineConfig,
    prompts: list[PromptRecord],
    *,
    dry_run: bool = False,
) -> PreflightReport:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        resources = discover_resources(config.paths.checker_resources)
    except PreflightError:
        raise
    except (OSError, UnicodeError, ValueError) as exc:
        raise PreflightError(
            "Impossibile leggere le risorse locali del checker.",
            (str(exc),),
        ) from exc
    errors.extend(schema_support_errors(resources.schema_path, resources.skill_path))

    if sys.version_info < (3, 11):
        errors.append(f"Python 3.11+ richiesto; in uso {sys.version.split()[0]}.")
    prompts_dir = config.paths.prompts
    if not prompts_dir.is_dir():
        errors.append(f"Cartella prompt non trovata: {prompts_dir}")
    elif not os.access(prompts_dir, os.R_OK | os.X_OK):
        errors.append(f"Cartella prompt non leggibile: {prompts_dir}")
    unreadable = [
        prompt.name
        for prompt in prompts
        if prompt.content is None and prompt.prompt_hash is None
    ]
    if unreadable:
        errors.append(f"File prompt non leggibili: {', '.join(sorted(unreadable))}")
    errors.extend(_validate_collisions(prompts))

    generated = config.paths.generated_labs
    project = config.paths.project_root
    overlaps = [
        label
        for label, input_path in (
            ("prompts", config.paths.prompts),
            ("checker_resources", config.paths.checker_resources),
        )
        if paths_overlap(generated, input_path)
    ]
    resolved_generated = generated.resolve(strict=False)
    resolved_project = project.resolve(strict=False)
    if resolved_generated in {
        Path("/").resolve(),
        Path.home().resolve(),
        resolved_project,
    }:
        errors.append(f"Root di output non sicura: {resolved_generated}")
    elif overlaps:
        errors.append(
            "La root di output si sovrappone agli input: " + ", ".join(overlaps)
        )
    elif not resolved_generated.is_relative_to(resolved_project):
        errors.append(
            "La root di output deve restare nel progetto: "
            f"{resolved_generated} (progetto: {resolved_project})"
        )
    elif dry_run:
        try:
            ensure_generated_root_managed(generated, initialize=False)
        except UnsafePathError as exc:
            errors.append(str(exc))
        parent = _nearest_existing_directory(generated)
        if parent is None or not os.access(parent, os.W_OK | os.X_OK):
            errors.append(f"Root di output non scrivibile: {generated}")
    else:
        try:
            ensure_generated_root_managed(generated, initialize=True)
            with tempfile.NamedTemporaryFile(dir=generated, prefix=".write-check-", delete=True) as probe:
                probe.write(b"ok")
                probe.flush()
        except (OSError, UnsafePathError) as exc:
            errors.append(f"Root di output non scrivibile ({generated}): {exc}")

    try:
        import yaml  # noqa: F401
    except ImportError:
        errors.append("Il modulo Python 'yaml' non è importabile.")
    if resources.schema_mode == "json-schema" and importlib.util.find_spec("jsonschema") is None:
        errors.append("Lo schema è JSON Schema ma 'jsonschema' non è importabile.")

    external_issues = warnings if dry_run else errors
    codex_path = shutil.which(config.codex.command)
    if codex_path is None:
        external_issues.append(f"Comando Codex non trovato: {config.codex.command}")
    elif dry_run:
        warnings.append("Dry-run: autenticazione e flag di Codex CLI non vengono verificati.")
    elif not dry_run:
        try:
            help_result = _run([config.codex.command, "exec", "--help"])
            required_flags = (
                "--config",
                "--sandbox",
                "--cd",
                "--json",
                "--output-last-message",
                "--ephemeral",
            )
            if help_result.returncode != 0 or any(flag not in help_result.stdout for flag in required_flags):
                errors.append("La versione di Codex CLI non espone tutti i flag richiesti.")
            auth_result = _run([config.codex.command, "login", "status"])
            auth_text = f"{auth_result.stdout}\n{auth_result.stderr}".casefold()
            if auth_result.returncode != 0 or "logged in" not in auth_text:
                errors.append("Codex CLI non risulta autenticato.")
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"Impossibile verificare Codex CLI: {exc}")

    checker_spec = importlib.util.find_spec("kathara_lab_checker")
    if checker_spec is None:
        external_issues.append("Il modulo 'kathara_lab_checker' non è importabile nell'interprete corrente.")
    else:
        try:
            checker_version = importlib.metadata.version("kathara-lab-checker")
        except importlib.metadata.PackageNotFoundError:
            checker_version = None
        if checker_version != "0.1.14":
            external_issues.append(
                "Versione kathara-lab-checker non supportata: "
                f"{checker_version or 'sconosciuta'} (richiesta 0.1.14)."
            )
        elif not _checker_documents_yaml(resources):
            external_issues.append("Il checker installato non documenta il supporto YAML/lab_inline.")
        elif dry_run:
            warnings.append("Dry-run: help della CLI kathara_lab_checker non invocato.")
        else:
            try:
                checker_help = _run([sys.executable, "-m", "kathara_lab_checker", "--help"])
                required = ("--config", "--labs", "--no-cache", "--report-type", "csv")
                if checker_help.returncode != 0 or any(token not in checker_help.stdout for token in required):
                    errors.append("La CLI kathara_lab_checker non supporta l'invocazione richiesta.")
            except (OSError, subprocess.TimeoutExpired) as exc:
                errors.append(f"Impossibile verificare kathara_lab_checker: {exc}")

    kathara_path = shutil.which("kathara")
    if kathara_path is None:
        external_issues.append("Comando Kathara non trovato.")
    elif dry_run:
        warnings.append("Dry-run: disponibilità del motore di container Kathara non verificata.")
    elif not dry_run:
        try:
            kathara_check = _run(["kathara", "check"], timeout=60)
            if kathara_check.returncode != 0:
                lines = [
                    line.strip()
                    for line in (kathara_check.stderr or kathara_check.stdout).splitlines()
                    if line.strip()
                ]
                critical = next(
                    (index for index, line in enumerate(lines) if "CRITICAL" in line.upper()),
                    None,
                )
                useful = lines[critical:] if critical is not None else lines[-3:]
                detail = " ".join(useful) if useful else f"exit code {kathara_check.returncode}"
                errors.append(f"Kathara/container engine non disponibile: {detail}")
        except (OSError, subprocess.TimeoutExpired) as exc:
            errors.append(f"Impossibile verificare Kathara/container engine: {exc}")

    return PreflightReport(resources, tuple(errors), tuple(warnings))
