from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError, UnsafePathError
from .paths import ensure_generated_root_managed, paths_overlap


@dataclass(frozen=True, slots=True)
class PathSettings:
    project_root: Path
    prompts: Path
    checker_resources: Path
    generated_labs: Path


@dataclass(frozen=True, slots=True)
class CodexSettings:
    command: str = "codex"
    sandbox: str = "workspace-write"
    timeout_seconds: int = 1800


@dataclass(frozen=True, slots=True)
class CheckerSettings:
    report_type: str = "csv"
    no_cache: bool = True
    timeout_seconds: int = 1800


@dataclass(frozen=True, slots=True)
class ProcessingSettings:
    continue_on_error: bool = True
    force: bool = False
    skip_completed: bool = True


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    paths: PathSettings
    codex: CodexSettings
    checker: CheckerSettings
    processing: ProcessingSettings
    config_path: Path


_SECTIONS: dict[str, set[str]] = {
    "paths": {"prompts", "checker_resources", "generated_labs"},
    "codex": {"command", "sandbox", "timeout_seconds"},
    "checker": {"report_type", "no_cache", "timeout_seconds"},
    "processing": {"continue_on_error", "force", "skip_completed"},
}


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ConfigurationError(f"La sezione '{label}' deve essere un mapping YAML.")
    return value


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ConfigurationError(f"'{label}' deve essere un intero positivo.")
    return value


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ConfigurationError(f"'{label}' deve essere true oppure false.")
    return value


def _resolve_project_path(root: Path, value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"'{label}' deve essere un path non vuoto.")
    raw = Path(value)
    resolved = (raw if raw.is_absolute() else root / raw).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ConfigurationError(f"'{label}' deve restare dentro la root del progetto: {resolved}") from exc
    return resolved


def _find_project_root(config_path: Path) -> Path:
    """Use the nearest package root, falling back to the config directory."""

    for candidate in (config_path.parent, *config_path.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate.resolve()
    return config_path.parent.resolve()


def load_config(path: Path | str = Path("pipeline.yaml")) -> PipelineConfig:
    config_path = Path(path).resolve()
    if not config_path.is_file():
        raise ConfigurationError(f"File di configurazione non trovato: {config_path}")
    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Impossibile leggere {config_path}: {exc}") from exc
    root_data = _mapping(loaded, "root")
    unknown_sections = set(root_data) - set(_SECTIONS)
    if unknown_sections:
        raise ConfigurationError(f"Sezioni sconosciute: {', '.join(sorted(unknown_sections))}")

    sections: dict[str, dict[str, Any]] = {}
    for name, allowed in _SECTIONS.items():
        section = _mapping(root_data.get(name), name)
        unknown = set(section) - allowed
        if unknown:
            raise ConfigurationError(
                f"Chiavi sconosciute in '{name}': {', '.join(sorted(unknown))}"
            )
        sections[name] = section

    project_root = _find_project_root(config_path)
    path_data = sections["paths"]
    paths = PathSettings(
        project_root=project_root,
        prompts=_resolve_project_path(project_root, path_data.get("prompts", "prompts_generates"), "paths.prompts"),
        checker_resources=_resolve_project_path(
            project_root,
            path_data.get("checker_resources", "kathara-lab-checker"),
            "paths.checker_resources",
        ),
        generated_labs=_resolve_project_path(
            project_root,
            path_data.get("generated_labs", "kathara-lab-generates"),
            "paths.generated_labs",
        ),
    )
    for input_label, input_path in (
        ("paths.prompts", paths.prompts),
        ("paths.checker_resources", paths.checker_resources),
    ):
        if paths_overlap(paths.generated_labs, input_path):
            raise ConfigurationError(
                "'paths.generated_labs' non può sovrapporsi a "
                f"'{input_label}': {paths.generated_labs} <-> {input_path}"
            )
    try:
        # Loading configuration must never create the marker, but it rejects a
        # populated root that has not demonstrably been created by this tool.
        ensure_generated_root_managed(paths.generated_labs, initialize=False)
    except UnsafePathError as exc:
        raise ConfigurationError(str(exc)) from exc

    codex_data = sections["codex"]
    command = codex_data.get("command", "codex")
    sandbox = codex_data.get("sandbox", "workspace-write")
    if not isinstance(command, str) or not command.strip() or any(ch.isspace() for ch in command):
        raise ConfigurationError("'codex.command' deve essere un singolo eseguibile.")
    if sandbox != "workspace-write":
        raise ConfigurationError(
            "'codex.sandbox' deve essere 'workspace-write' perché Codex genera file nel workspace."
        )
    codex = CodexSettings(
        command=command,
        sandbox=sandbox,
        timeout_seconds=_positive_int(codex_data.get("timeout_seconds", 1800), "codex.timeout_seconds"),
    )

    checker_data = sections["checker"]
    report_type = checker_data.get("report_type", "csv")
    if report_type != "csv":
        raise ConfigurationError("Questa pipeline richiede checker.report_type: csv.")
    no_cache = _boolean(checker_data.get("no_cache", True), "checker.no_cache")
    if not no_cache:
        raise ConfigurationError(
            "'checker.no_cache' deve essere true: ogni laboratorio deve essere testato una sola volta senza report in cache."
        )
    checker = CheckerSettings(
        report_type=report_type,
        no_cache=no_cache,
        timeout_seconds=_positive_int(
            checker_data.get("timeout_seconds", 1800), "checker.timeout_seconds"
        ),
    )

    processing_data = sections["processing"]
    processing = ProcessingSettings(
        continue_on_error=_boolean(
            processing_data.get("continue_on_error", True), "processing.continue_on_error"
        ),
        force=_boolean(processing_data.get("force", False), "processing.force"),
        skip_completed=_boolean(
            processing_data.get("skip_completed", True), "processing.skip_completed"
        ),
    )
    return PipelineConfig(paths, codex, checker, processing, config_path)
