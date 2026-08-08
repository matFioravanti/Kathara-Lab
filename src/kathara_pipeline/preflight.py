from __future__ import annotations

import importlib.util
import shutil
import subprocess
from pathlib import Path

from .config import PipelineConfig
from .exceptions import ResourceError
from .models import PromptRecord, ResourceFiles
from .paths import paths_overlap
from .resource_discovery import discover_resources


class PreflightResult:
    def __init__(self, resources: ResourceFiles, warnings: list[str] | None = None):
        self.resources = resources
        self.warnings = warnings or []


def _probe(command: list[str], label: str, *, timeout: int = 60) -> None:
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ResourceError(f"Preflight {label} fallito: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise ResourceError(f"Preflight {label} fallito (exit {result.returncode}): {detail[:1000]}")


def run_preflight(config: PipelineConfig, prompts_dir: Path, prompts: list[PromptRecord], *, dry_run: bool = False) -> PreflightResult:
    resources = discover_resources(config.paths.resources)
    prompt_root = Path(prompts_dir).expanduser().resolve(strict=False)
    output = config.paths.output.expanduser().resolve(strict=False)
    if paths_overlap(prompt_root, output):
        raise ResourceError("La directory output non può coincidere o sovrapporsi alla directory dei prompt.")
    if paths_overlap(resources.root, output):
        raise ResourceError("La directory output non può sovrapporsi alle risorse del framework.")
    if not prompts:
        raise ResourceError("Nessun prompt .md/.txt trovato nella directory indicata.")
    bad = [item.name for item in prompts if item.decode_error or item.empty]
    if bad:
        raise ResourceError("Prompt non validi/vuoti: " + ", ".join(bad))

    warnings: list[str] = []
    missing_agent = shutil.which(config.generation.command) is None
    missing_kathara = shutil.which("kathara") is None
    missing_checker = importlib.util.find_spec("kathara_lab_checker") is None
    for condition, message in (
        (missing_agent, f"CLI provider non trovata nel PATH: {config.generation.command}"),
        (missing_checker, "Modulo kathara_lab_checker non installato nell'interprete Python corrente."),
        (missing_kathara, "Comando kathara non trovato nel PATH."),
    ):
        if condition:
            if dry_run:
                warnings.append(message)
            else:
                raise ResourceError(message)

    # Dry-run is strictly side-effect free and never starts external processes.
    if dry_run:
        return PreflightResult(resources, warnings)

    _probe(["kathara", "check"], "Kathara/backend")
    provider = config.generation.provider
    if provider == "codex":
        _probe([config.generation.command, "login", "status"], "Codex authentication")
        _probe([config.generation.command, "exec", "--help"], "Codex exec flags")
    elif provider == "claude":
        _probe([config.generation.command, "--version"], "Claude version")
        _probe([config.generation.command, "auth", "status"], "Claude authentication")
    elif provider == "gemini":
        # Gemini authentication may be confirmed by the first headless invocation; do not
        # consume a model call during preflight. Verify only the local CLI installation.
        _probe([config.generation.command, "--version"], "Gemini version")
        warnings.append("Gemini CLI: autenticazione verificata dalla prima chiamata headless; il preflight non consuma quota.")
    return PreflightResult(resources, warnings)
