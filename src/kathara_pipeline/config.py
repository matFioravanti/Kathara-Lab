from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class PathSettings:
    project_root: Path
    resources: Path
    output: Path


@dataclass(frozen=True, slots=True)
class GenerationSettings:
    provider: str = "codex"
    command: str = "codex"
    model: str | None = "gpt-5.6-terra"
    reasoning_effort: str | None = "low"
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
    keep_workspaces: bool = False
    resume_from: str | None = None


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    paths: PathSettings
    generation: GenerationSettings
    checker: CheckerSettings
    processing: ProcessingSettings
    config_path: Path

    def with_overrides(
        self,
        *,
        output_dir: Path | None = None,
        force: bool | None = None,
        resume_from: str | None = None,
    ) -> "PipelineConfig":
        paths = self.paths if output_dir is None else replace(self.paths, output=output_dir.resolve())
        processing_kwargs = {}
        if force is not None:
            processing_kwargs["force"] = force
        if resume_from is not None:
            processing_kwargs["resume_from"] = resume_from
        
        if processing_kwargs:
            processing = replace(self.processing, **processing_kwargs)
        else:
            processing = self.processing
            
        return replace(self, paths=paths, processing=processing)


_SECTIONS = {
    "paths": {"resources", "output"},
    "generation": {
        "provider", "command", "model", "reasoning_effort", "sandbox", "timeout_seconds"
    },
    "checker": {"report_type", "no_cache", "timeout_seconds"},
    "processing": {"continue_on_error", "force", "skip_completed", "keep_workspaces"},
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


def _string(value: Any, label: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"'{label}' deve essere una stringa non vuota.")
    return value.strip()


def _find_project_root(config_path: Path) -> Path:
    for candidate in (config_path.parent, *config_path.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate.resolve()
    return config_path.parent.resolve()


def _project_path(root: Path, value: Any, label: str) -> Path:
    text = _string(value, label)
    assert text is not None
    raw = Path(text).expanduser()
    return (raw if raw.is_absolute() else root / raw).resolve(strict=False)


def load_config(path: Path | str = Path("pipeline.yaml")) -> PipelineConfig:
    config_path = Path(path).expanduser().resolve(strict=False)
    if not config_path.is_file():
        raise ConfigurationError(f"File di configurazione non trovato: {config_path}")
    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Impossibile leggere {config_path}: {exc}") from exc
    root = _mapping(loaded, "root")
    unknown_sections = set(root) - set(_SECTIONS)
    if unknown_sections:
        raise ConfigurationError("Sezioni sconosciute: " + ", ".join(sorted(unknown_sections)))
    sections: dict[str, dict[str, Any]] = {}
    for name, allowed in _SECTIONS.items():
        section = _mapping(root.get(name), name)
        unknown = set(section) - allowed
        if unknown:
            raise ConfigurationError(f"Chiavi sconosciute in '{name}': {', '.join(sorted(unknown))}")
        sections[name] = section

    project_root = _find_project_root(config_path)
    paths_data = sections["paths"]
    paths = PathSettings(
        project_root=project_root,
        resources=_project_path(project_root, paths_data.get("resources", "resources"), "paths.resources"),
        output=_project_path(project_root, paths_data.get("output", "results"), "paths.output"),
    )

    generation_data = sections["generation"]
    provider = str(generation_data.get("provider", "codex")).strip().casefold()
    if provider not in {"codex", "gemini", "claude"}:
        raise ConfigurationError("generation.provider deve essere codex, gemini oppure claude.")
    default_commands = {"codex": "codex", "gemini": "gemini", "claude": "claude"}
    command = _string(generation_data.get("command", default_commands[provider]), "generation.command")
    assert command is not None
    if any(char.isspace() for char in command):
        raise ConfigurationError("generation.command deve essere un singolo eseguibile.")
    model = generation_data.get("model", "gpt-5.6-terra" if provider == "codex" else None)
    if model is not None:
        model = _string(model, "generation.model", optional=True)
    reasoning = generation_data.get("reasoning_effort", "low" if provider == "codex" else None)
    if reasoning is not None:
        reasoning = _string(reasoning, "generation.reasoning_effort", optional=True)
    sandbox = _string(generation_data.get("sandbox", "workspace-write"), "generation.sandbox")
    assert sandbox is not None
    generation = GenerationSettings(
        provider=provider,
        command=command,
        model=model,
        reasoning_effort=reasoning,
        sandbox=sandbox,
        timeout_seconds=_positive_int(generation_data.get("timeout_seconds", 1800), "generation.timeout_seconds"),
    )

    checker_data = sections["checker"]
    report_type = str(checker_data.get("report_type", "csv")).strip().casefold()
    if report_type != "csv":
        raise ConfigurationError("Il framework richiede checker.report_type: csv.")
    no_cache = _boolean(checker_data.get("no_cache", True), "checker.no_cache")
    if not no_cache:
        raise ConfigurationError("checker.no_cache deve essere true per esperimenti indipendenti.")
    checker = CheckerSettings(
        report_type=report_type,
        no_cache=True,
        timeout_seconds=_positive_int(checker_data.get("timeout_seconds", 1800), "checker.timeout_seconds"),
    )

    processing_data = sections["processing"]
    processing = ProcessingSettings(
        continue_on_error=_boolean(processing_data.get("continue_on_error", True), "processing.continue_on_error"),
        force=_boolean(processing_data.get("force", False), "processing.force"),
        skip_completed=_boolean(processing_data.get("skip_completed", True), "processing.skip_completed"),
        keep_workspaces=_boolean(processing_data.get("keep_workspaces", False), "processing.keep_workspaces"),
    )
    return PipelineConfig(paths, generation, checker, processing, config_path)
