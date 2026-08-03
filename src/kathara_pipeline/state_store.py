from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .exceptions import ManifestError


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase SHA-256 hex digest for a byte string."""

    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Hash text using the pipeline's canonical UTF-8 encoding."""

    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Hash a regular file without loading it entirely into memory."""

    if chunk_size <= 0:
        raise ValueError("chunk_size deve essere maggiore di zero")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_directory(root: Path) -> dict[str, str]:
    """Return deterministic hashes for files and explicit symlink targets."""

    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise NotADirectoryError(str(root))

    entries = sorted(
        (
            path
            for path in resolved_root.rglob("*")
            if path.is_file() or path.is_symlink()
        ),
        key=lambda path: path.relative_to(resolved_root).as_posix(),
    )
    return {
        path.relative_to(resolved_root).as_posix(): (
            sha256_bytes(b"symlink\0" + str(path.readlink()).encode("utf-8"))
            if path.is_symlink()
            else sha256_file(path)
        )
        for path in entries
    }


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    raise TypeError(f"Oggetto non serializzabile in JSON: {type(value).__name__}")


def read_json(path: Path) -> dict[str, Any] | None:
    """Read one JSON mapping, returning ``None`` when it does not exist."""

    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(
            f"Impossibile leggere il manifest {path}",
            details=(str(exc),),
        ) from exc
    if not isinstance(value, dict):
        raise ManifestError(
            f"Il manifest {path} deve contenere un oggetto JSON",
            details=(f"Tipo trovato: {type(value).__name__}",),
        )
    return value


def write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically write a JSON mapping using a temporary sibling file."""

    temporary_path: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(
                dict(payload),
                stream,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                default=_json_default,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except (OSError, TypeError, ValueError) as exc:
        raise ManifestError(
            f"Impossibile scrivere atomicamente il manifest {path}",
            details=(str(exc),),
        ) from exc
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


class StateStore:
    """Small manifest repository bound to one job's manifest path."""

    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path

    def read(self) -> dict[str, Any] | None:
        return read_json(self.manifest_path)

    def write(self, payload: Mapping[str, Any]) -> None:
        write_json_atomic(self.manifest_path, payload)
