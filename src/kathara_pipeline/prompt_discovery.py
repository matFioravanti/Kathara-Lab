from __future__ import annotations

import re
from pathlib import Path

from .exceptions import PromptDiscoveryError, UnsafePathError
from .models import PromptRecord
from .paths import experiment_id_from_prompt
from .state_store import sha256_bytes

_SUPPORTED_SUFFIXES = {".md", ".txt"}
_NATURAL_PARTS = re.compile(r"(\d+)")


def natural_sort_key(name: str):
    parts: list[tuple[int, int | str]] = []
    for part in _NATURAL_PARTS.split(name.casefold()):
        if not part:
            continue
        parts.append((0, int(part)) if part.isdigit() else (1, part))
    return tuple(parts), name.casefold(), name


def discover_prompts(prompts_dir: Path) -> list[PromptRecord]:
    directory = Path(prompts_dir).expanduser().resolve(strict=False)
    if not directory.exists():
        raise PromptDiscoveryError(f"Directory dei prompt inesistente: {directory}")
    if not directory.is_dir() or directory.is_symlink():
        raise PromptDiscoveryError(f"Il path dei prompt non è una directory regolare: {directory}")
    candidates: list[Path] = []
    try:
        for entry in directory.iterdir():
            if entry.name.startswith(".") or entry.suffix.casefold() not in _SUPPORTED_SUFFIXES:
                continue
            if entry.is_symlink():
                raise PromptDiscoveryError(f"I prompt non possono essere symlink: {entry.name}")
            if entry.is_file():
                candidates.append(entry)
    except OSError as exc:
        raise PromptDiscoveryError(f"Impossibile leggere {directory}: {exc}") from exc
    records: list[PromptRecord] = []
    ids: dict[str, str] = {}
    for path in sorted(candidates, key=lambda item: natural_sort_key(item.name)):
        try:
            experiment_id = experiment_id_from_prompt(path)
        except UnsafePathError as exc:
            raise PromptDiscoveryError(str(exc)) from exc
        folded = experiment_id.casefold()
        if folded in ids:
            # Different external filenames can normalize to the same safe id
            # (for example "Lab A.md" and "Lab, A.md").  Keep discovery
            # automatic by adding a stable suffix derived from the filename.
            suffix = sha256_bytes(path.name.encode("utf-8"))[:10]
            experiment_id = f"{experiment_id}_{suffix}"
            folded = experiment_id.casefold()
            counter = 2
            while folded in ids:
                experiment_id = f"{experiment_id}_{counter}"
                folded = experiment_id.casefold()
                counter += 1
        ids[folded] = path.name
        try:
            raw = path.read_bytes()
        except OSError as exc:
            records.append(PromptRecord(path, path.name, experiment_id, None, None, str(exc)))
            continue
        digest = sha256_bytes(raw)
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            records.append(
                PromptRecord(path, path.name, experiment_id, None, digest, f"UTF-8 non valido: {exc}")
            )
            continue
        records.append(PromptRecord(path, path.name, experiment_id, text, digest))
    return records
