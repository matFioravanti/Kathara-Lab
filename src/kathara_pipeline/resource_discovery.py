from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml

from .exceptions import PreflightError
from .models import ResourceFiles


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _unique(candidates: list[Path], label: str, root: Path) -> Path:
    resolved_root = root.resolve()
    resolved_candidates: set[Path] = set()
    for path in candidates:
        if path.is_symlink():
            raise PreflightError(f"Un symlink non è consentito per {label}: {path}")
        resolved = path.resolve()
        if not resolved.is_relative_to(resolved_root):
            raise PreflightError(f"File esterno alla root delle risorse per {label}: {resolved}")
        if resolved.is_file():
            resolved_candidates.add(resolved)
    unique = sorted(resolved_candidates, key=lambda item: str(item))
    if not unique:
        raise PreflightError(f"Nessun file utilizzabile trovato per {label}.")
    if len(unique) > 1:
        listed = ", ".join(str(path) for path in unique)
        raise PreflightError(f"Più candidati ambigui per {label}: {listed}")
    return unique[0]


def _is_json_schema(path: Path) -> bool:
    if path.suffix.casefold() not in {".json", ".yaml", ".yml"}:
        return False
    try:
        text = path.read_text(encoding="utf-8")
        parsed: Any = json.loads(text) if path.suffix.casefold() == ".json" else yaml.safe_load(text)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError):
        return False
    if not isinstance(parsed, dict):
        return False
    return "$schema" in parsed or (
        parsed.get("type") == "object" and isinstance(parsed.get("properties"), dict)
    )


def discover_resources(root: Path) -> ResourceFiles:
    root = root.resolve()
    if not root.is_dir():
        raise PreflightError(f"Cartella risorse del checker non trovata: {root}")

    exact_skills = [path for path in root.rglob("*") if path.is_file() and path.name.casefold() == "skill.md"]
    if exact_skills:
        skill = _unique(exact_skills, "la Skill", root)
    else:
        fallback = [
            path
            for path in root.iterdir()
            if path.is_file()
            and path.suffix.casefold() == ".md"
            and path.name.casefold() != "readme.md"
        ]
        skill = _unique(fallback, "la Skill", root)

    exact_schema = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.name.casefold() == "config-schema.json"
    ]
    if exact_schema:
        schema = _unique(exact_schema, "lo schema di configurazione", root)
    else:
        conventional = [
            path
            for path in root.rglob("*")
            if path.is_file()
            and path.stem.casefold() == "config-schema"
            and path.suffix.casefold() in {".json", ".yaml", ".yml", ".md"}
        ]
        if conventional:
            schema = _unique(conventional, "lo schema di configurazione", root)
        else:
            skill_text = skill.read_text(encoding="utf-8")
            linked: list[Path] = []
            for match in re.finditer(r"(?P<path>[A-Za-z0-9_./-]*config-schema\.(?:json|ya?ml|md))", skill_text, re.I):
                candidate = skill.parent / match.group("path")
                if candidate.is_file() or candidate.is_symlink():
                    linked.append(candidate)
            if linked:
                schema = _unique(linked, "lo schema indicato dalla Skill", root)
            else:
                fallback_schema = [
                    path
                    for path in skill.parent.iterdir()
                    if path.is_file() and path.suffix.casefold() in {".json", ".yaml", ".yml"}
                ]
                schema = _unique(fallback_schema, "lo schema di configurazione", root)

    examples_candidates = [root / "examples", schema.parent / "examples"]
    examples: Path | None = None
    for path in examples_candidates:
        if path.is_symlink():
            raise PreflightError(f"La directory examples non può essere un symlink: {path}")
        if path.is_dir():
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                raise PreflightError(f"Directory examples esterna alle risorse: {resolved}")
            examples = resolved
            break
    mode = "json-schema" if _is_json_schema(schema) else "documented-structure"
    return ResourceFiles(
        root=root,
        skill_path=skill,
        schema_path=schema,
        examples_path=examples,
        skill_hash=_hash_file(skill),
        schema_hash=_hash_file(schema),
        schema_mode=mode,
    )
