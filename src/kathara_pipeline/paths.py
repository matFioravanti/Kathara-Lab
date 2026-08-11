from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from pathlib import Path

from .exceptions import UnsafePathError
from .models import ExperimentPaths, Variant, VariantPaths

_MARKER = ".kathara-experiment-root"
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_UNSAFE_ID_CHARS = re.compile(r"[^A-Za-z0-9_.-]+")
_MAX_EXPERIMENT_ID_LENGTH = 120


def sanitize_experiment_id(value: str) -> str:
    cleaned = value.strip().replace(" ", "_")
    if not cleaned or not _SAFE_ID.fullmatch(cleaned):
        raise UnsafePathError(f"Experiment id non sicuro: {value!r}")
    if cleaned in {".", ".."}:
        raise UnsafePathError(f"Experiment id non sicuro: {value!r}")
    return cleaned


def experiment_id_from_prompt(path: Path) -> str:
    """Build a deterministic filesystem-safe id from an arbitrary prompt filename.

    Prompt files are external input and may legitimately contain spaces, commas,
    parentheses, accents, or other punctuation.  Those characters must not make
    discovery fail merely because the experiment result needs a safe directory
    name.  Internal ids are still validated strictly by ``sanitize_experiment_id``.
    """
    original = path.stem.strip()
    normalized = unicodedata.normalize("NFKD", original)
    ascii_value = normalized.encode("ascii", errors="ignore").decode("ascii")
    cleaned = _UNSAFE_ID_CHARS.sub("_", ascii_value)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._-")

    digest = hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:10]
    if not cleaned:
        cleaned = f"experiment_{digest}"
    if len(cleaned) > _MAX_EXPERIMENT_ID_LENGTH:
        keep = _MAX_EXPERIMENT_ID_LENGTH - len(digest) - 1
        cleaned = f"{cleaned[:keep].rstrip('._-')}_{digest}"

    return sanitize_experiment_id(cleaned)


def paths_overlap(left: Path, right: Path) -> bool:
    a = left.expanduser().resolve(strict=False)
    b = right.expanduser().resolve(strict=False)
    return a == b or a.is_relative_to(b) or b.is_relative_to(a)


def ensure_output_root(output_root: Path, *, initialize: bool) -> None:
    root = output_root.expanduser().resolve(strict=False)
    marker = root / _MARKER
    if not root.exists():
        if initialize:
            root.mkdir(parents=True)
            marker.write_text("kathara-experiment-framework\n", encoding="utf-8")
        return
    if not root.is_dir() or root.is_symlink():
        raise UnsafePathError(f"Output root non valida: {root}")
    entries = [entry for entry in root.iterdir() if entry.name != _MARKER]
    if marker.is_file() and not marker.is_symlink():
        return
    if entries:
        raise UnsafePathError(
            f"Output root già popolata ma priva del marker {_MARKER}: {root}"
        )
    if initialize:
        marker.write_text("kathara-experiment-framework\n", encoding="utf-8")


def safe_rmtree(target: Path, output_root: Path) -> None:
    root = output_root.expanduser().resolve(strict=False)
    resolved = target.expanduser().resolve(strict=False)
    if resolved == root or not resolved.is_relative_to(root):
        raise UnsafePathError(f"Cancellazione non sicura: {resolved}")
    if target.is_symlink():
        raise UnsafePathError(f"Non posso cancellare un symlink come albero: {target}")
    if resolved.exists():
        shutil.rmtree(resolved)


def _variant_paths(root: Path, variant: Variant) -> VariantPaths:
    variant_root = root / variant.value
    checker_run = variant_root / "checker-run"
    labs_dir = checker_run / "labs"
    correction_dir = variant_root / "correction"
    return VariantPaths(
        root=variant_root,
        source=variant_root / "source",
        source_failed=variant_root / "source_failed",
        checker_run=checker_run,
        labs_dir=labs_dir,
        candidate=labs_dir / "candidate",
        reports=variant_root / "reports",
        logs=variant_root / "logs",
        manifest=variant_root / "manifest.json",
        workspace=root / ".workspaces" / variant.value,
        correction_dir=correction_dir,
        correction=correction_dir / "correction.yaml",
        correction_logs=correction_dir / "logs",
        correction_workspace=root / ".workspaces" / f"correction_{variant.value}",
    )


def build_experiment_paths(output_root: Path, experiment_id: str) -> ExperimentPaths:
    safe_id = sanitize_experiment_id(experiment_id)
    root = output_root.expanduser().resolve(strict=False) / safe_id
    return ExperimentPaths(
        root=root,
        prompt=root / "prompt.md",
        comparison=root / "comparison.json",
        comparison_csv=root / "comparison.csv",
        experiment_manifest=root / "experiment.json",
        with_skill=_variant_paths(root, Variant.WITH_SKILL),
        without_skill=_variant_paths(root, Variant.WITHOUT_SKILL),
    )
