from __future__ import annotations

import re
from pathlib import Path

from .exceptions import PromptDiscoveryError, UnsafePathError
from .models import PromptRecord
from .paths import ensure_no_lab_id_collisions, lab_id_from_prompt
from .state_store import sha256_bytes


_SUPPORTED_SUFFIXES = {".md", ".txt"}
_NATURAL_PARTS = re.compile(r"(\d+)")


def natural_sort_key(name: str) -> tuple[tuple[tuple[int, int | str], ...], str]:
    """Build a total, deterministic natural-order key for one filename."""

    parts: list[tuple[int, int | str]] = []
    for part in _NATURAL_PARTS.split(name):
        if not part:
            continue
        if part.isdigit():
            parts.append((0, int(part)))
        else:
            parts.append((1, part))
    return tuple(parts), name


def _candidate_paths(prompts_dir: Path) -> tuple[Path, ...]:
    try:
        if not prompts_dir.exists():
            raise PromptDiscoveryError(f"Directory dei prompt inesistente: {prompts_dir}")
        if not prompts_dir.is_dir():
            raise PromptDiscoveryError(f"Il path dei prompt non è una directory: {prompts_dir}")
        entries = tuple(prompts_dir.iterdir())
        unsafe_links = sorted(
            (
                entry.name
                for entry in entries
                if not entry.name.startswith(".")
                and entry.suffix.lower() in _SUPPORTED_SUFFIXES
                and entry.is_symlink()
            )
        )
        if unsafe_links:
            raise PromptDiscoveryError(
                "I prompt devono essere file regolari, non symlink: "
                + ", ".join(unsafe_links)
            )
        candidates = tuple(
            entry
            for entry in entries
            if not entry.name.startswith(".")
            and entry.suffix.lower() in _SUPPORTED_SUFFIXES
            and entry.is_file()
            and not entry.is_symlink()
        )
    except PromptDiscoveryError:
        raise
    except OSError as exc:
        raise PromptDiscoveryError(
            f"Impossibile elencare la directory dei prompt {prompts_dir}: {exc}"
        ) from exc
    return tuple(sorted(candidates, key=lambda path: natural_sort_key(path.name)))


def _read_prompt(path: Path, lab_id: str) -> PromptRecord:
    try:
        raw_content = path.read_bytes()
    except OSError as exc:
        return PromptRecord(
            path=path,
            name=path.name,
            lab_id=lab_id,
            content=None,
            prompt_hash=None,
            decode_error=f"Errore di lettura: {exc}",
        )

    prompt_hash = sha256_bytes(raw_content)
    try:
        content = raw_content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return PromptRecord(
            path=path,
            name=path.name,
            lab_id=lab_id,
            content=None,
            prompt_hash=prompt_hash,
            decode_error=(
                "Errore di decodifica UTF-8 "
                f"ai byte {exc.start}-{exc.end}: {exc.reason}"
            ),
        )

    return PromptRecord(
        path=path,
        name=path.name,
        lab_id=lab_id,
        content=content,
        prompt_hash=prompt_hash,
    )


def discover_prompts(prompts_dir: Path) -> list[PromptRecord]:
    """Discover supported direct children and preserve per-file read errors.

    Empty prompts remain in the result so the orchestrator can persist a
    terminal ``skipped`` job. UTF-8 failures likewise remain as records with a
    ``decode_error`` instead of aborting discovery of later prompts.
    """

    records: list[PromptRecord] = []
    for path in _candidate_paths(prompts_dir):
        try:
            lab_id = lab_id_from_prompt(path)
        except UnsafePathError as exc:
            raise PromptDiscoveryError(
                f"Nome prompt non sicuro {path.name!r}: {exc}"
            ) from exc
        records.append(_read_prompt(path, lab_id))

    ensure_no_lab_id_collisions(records)
    return records
