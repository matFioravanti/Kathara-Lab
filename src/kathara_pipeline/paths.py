from __future__ import annotations

import os
import re
import shutil
import tempfile
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from .exceptions import PromptDiscoveryError, UnsafePathError
from .models import JobPaths, PromptRecord


_UNSAFE_NAME_CHARACTERS = re.compile(r"[^A-Za-z0-9._-]+")
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}

# A root is considered managed only when this regular file contains exactly this
# value.  It deliberately lives in the root, rather than in a job directory,
# so every destructive operation has one unambiguous ownership boundary.
GENERATED_ROOT_MARKER = ".kathara-pipeline-root"
GENERATED_ROOT_MARKER_CONTENT = "kathara-pipeline-generated-labs-v1\n"


def sanitize_lab_id(raw_name: str) -> str:
    """Return a portable lab identifier or reject an unsafe input name.

    Path separators, control characters and parent-directory references are
    rejected rather than silently rewritten. Other non-portable characters are
    normalized to ``-`` so that collision detection can happen before any job
    directory is created.
    """

    if not isinstance(raw_name, str) or not raw_name.strip():
        raise UnsafePathError("Il nome del laboratorio non può essere vuoto")
    if "/" in raw_name or "\\" in raw_name:
        raise UnsafePathError(f"Il nome del laboratorio contiene separatori di path: {raw_name!r}")
    if raw_name.strip() in {".", ".."}:
        raise UnsafePathError(f"Riferimento a directory non consentito: {raw_name!r}")
    if any(unicodedata.category(character) == "Cc" for character in raw_name):
        raise UnsafePathError(f"Il nome del laboratorio contiene caratteri di controllo: {raw_name!r}")

    normalized = unicodedata.normalize("NFKD", raw_name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    sanitized = _UNSAFE_NAME_CHARACTERS.sub("-", ascii_name.strip())
    sanitized = re.sub(r"-+", "-", sanitized).strip(" .-_")

    if not sanitized or sanitized in {".", ".."}:
        raise UnsafePathError(f"La sanitizzazione produce un nome vuoto: {raw_name!r}")

    reserved_stem = sanitized.split(".", maxsplit=1)[0].upper()
    if reserved_stem in _WINDOWS_RESERVED_NAMES:
        raise UnsafePathError(f"Nome riservato dal sistema operativo: {raw_name!r}")
    return sanitized


def lab_id_from_prompt(prompt_path: Path) -> str:
    """Derive a lab identifier from a prompt filename without its suffix."""

    filename = prompt_path.name
    stem = Path(filename).stem
    if not stem or stem == filename and filename in {".", ".."}:
        raise UnsafePathError(f"Nome file prompt non valido: {filename!r}")
    return sanitize_lab_id(stem)


def detect_lab_id_collisions(
    prompts: Iterable[PromptRecord],
) -> dict[str, tuple[Path, ...]]:
    """Return lab-id collisions using portable case-insensitive semantics."""

    grouped: dict[str, set[Path]] = defaultdict(set)
    identifiers: dict[str, set[str]] = defaultdict(set)
    for prompt in prompts:
        portable_id = prompt.lab_id.casefold()
        grouped[portable_id].add(prompt.path)
        identifiers[portable_id].add(prompt.lab_id)

    collisions: dict[str, tuple[Path, ...]] = {}
    for portable_id, paths in sorted(grouped.items()):
        if len(paths) <= 1:
            continue
        display_id = " / ".join(
            sorted(identifiers[portable_id], key=lambda value: (value.casefold(), value))
        )
        collisions[display_id] = tuple(sorted(paths, key=lambda path: str(path)))
    return collisions


def ensure_no_lab_id_collisions(prompts: Iterable[PromptRecord]) -> None:
    """Raise a preflight-friendly discovery error for sanitized-id collisions."""

    collisions = detect_lab_id_collisions(prompts)
    if not collisions:
        return
    details = "; ".join(
        f"{lab_id}: {', '.join(path.name for path in paths)}"
        for lab_id, paths in collisions.items()
    )
    raise PromptDiscoveryError(f"Collisioni tra lab-id sanitizzati: {details}")


def _is_same_or_ancestor(candidate: Path, reference: Path) -> bool:
    return candidate == reference or reference.is_relative_to(candidate)


def _same_file(left: Path, right: Path) -> bool:
    """Return whether two existing paths identify the same filesystem object."""

    try:
        return left.samefile(right)
    except OSError:
        return False


def _existing_ancestor(path: Path) -> Path | None:
    candidate = path.expanduser()
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate if candidate.exists() else None


def _filesystem_is_case_insensitive(path: Path) -> bool:
    """Probe an existing path without writing to determine case semantics."""

    candidate = _existing_ancestor(path)
    while candidate is not None and candidate != candidate.parent:
        alternate_name = candidate.name.swapcase()
        if alternate_name != candidate.name and _same_file(
            candidate, candidate.with_name(alternate_name)
        ):
            return True
        candidate = candidate.parent
    return False


def _casefolded_is_same_or_ancestor(candidate: Path, reference: Path) -> bool:
    candidate_parts = tuple(part.casefold() for part in candidate.parts)
    reference_parts = tuple(part.casefold() for part in reference.parts)
    return (
        len(candidate_parts) <= len(reference_parts)
        and candidate_parts == reference_parts[: len(candidate_parts)]
    )


def paths_overlap(left: Path, right: Path) -> bool:
    """Return whether two paths overlap after filesystem-aware canonicalization.

    ``Path.resolve()`` handles aliases in existing ancestors, while ``samefile``
    catches filesystem aliases (including case-insensitive macOS volumes) when
    both paths already exist.  This is intentionally shared by configuration
    and preflight checks to prevent the two guards from drifting apart.
    """

    if _same_file(left, right):
        return True
    resolved_left = left.expanduser().resolve(strict=False)
    resolved_right = right.expanduser().resolve(strict=False)
    if _is_same_or_ancestor(resolved_left, resolved_right) or _is_same_or_ancestor(
        resolved_right, resolved_left
    ):
        return True
    if not (
        _filesystem_is_case_insensitive(resolved_left)
        or _filesystem_is_case_insensitive(resolved_right)
    ):
        return False
    return _casefolded_is_same_or_ancestor(
        resolved_left, resolved_right
    ) or _casefolded_is_same_or_ancestor(resolved_right, resolved_left)


def _marker_path(generated_root: Path) -> Path:
    return generated_root / GENERATED_ROOT_MARKER


def _first_symlink_component(path: Path) -> Path | None:
    """Return the first symlink in an absolute path without resolving it."""

    absolute = path.expanduser().absolute()
    for component in (*reversed(absolute.parents), absolute):
        if component.is_symlink():
            return component
    return None


def _write_generated_root_marker_atomically(root: Path) -> None:
    """Install the ownership marker without leaving a partial marker on failure."""

    marker = _marker_path(root)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=root.parent,
            prefix=f".{root.name}.marker-",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(GENERATED_ROOT_MARKER_CONTENT)
            stream.flush()
            os.fsync(stream.fileno())

        symlink_component = _first_symlink_component(root)
        if symlink_component is not None:
            raise UnsafePathError(
                "La root generata non può attraversare symlink durante l'inizializzazione: "
                f"{symlink_component}"
            )
        entries = list(root.iterdir())
        if entries:
            # A concurrent initializer may already have installed the same
            # marker. Any other new entry means the empty-root premise changed.
            if (
                len(entries) == 1
                and entries[0] == marker
                and not marker.is_symlink()
                and marker.is_file()
                and marker.read_text(encoding="utf-8") == GENERATED_ROOT_MARKER_CONTENT
            ):
                return
            raise UnsafePathError(
                f"La root di output è cambiata durante l'inizializzazione: {root}"
            )
        os.replace(temporary, marker)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def ensure_generated_root_managed(
    generated_root: Path, *, initialize: bool = False
) -> None:
    """Verify, and optionally initialize, the generated-labs ownership marker.

    Missing or empty roots can safely be initialized.  Any non-empty root needs
    the exact regular marker; this prevents a configuration typo from turning a
    source, test, or repository directory into a deletion target.  ``dry-run``
    callers pass ``initialize=False`` and therefore never write the marker.
    """

    root = generated_root.expanduser().absolute()
    symlink_component = _first_symlink_component(root)
    if symlink_component is not None:
        raise UnsafePathError(
            "La root generata non può attraversare symlink: "
            f"{symlink_component} (root richiesta: {root})"
        )
    if root.exists() and not root.is_dir():
        raise UnsafePathError(f"La root generata non è una directory: {root}")
    if not root.exists():
        if not initialize:
            return
        root.mkdir(parents=True, exist_ok=True)

    entries = list(root.iterdir())
    marker = _marker_path(root)
    if not entries:
        if initialize:
            _write_generated_root_marker_atomically(root)
        return
    if marker.is_symlink() or not marker.is_file():
        raise UnsafePathError(
            "La root di output non è gestita dalla pipeline: "
            f"marker regolare '{GENERATED_ROOT_MARKER}' mancante o non valido in {root}"
        )
    try:
        marker_contents = marker.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise UnsafePathError(f"Impossibile verificare il marker della root di output: {exc}") from exc
    if marker_contents != GENERATED_ROOT_MARKER_CONTENT:
        raise UnsafePathError(
            "La root di output non è gestita dalla pipeline: "
            f"contenuto non valido di '{GENERATED_ROOT_MARKER}' in {root}"
        )


def assert_safe_destructive_path(
    target: Path,
    generated_root: Path,
    *,
    project_root: Path | None = None,
    home: Path | None = None,
) -> Path:
    """Resolve and validate a directory before a destructive operation.

    Only strict descendants of ``generated_root`` are accepted. The generated
    root itself, project/home roots, filesystem root, escaping ``..`` paths and
    symlinks resolving outside the generated root are rejected.
    """

    ensure_generated_root_managed(generated_root, initialize=False)

    resolved_root = generated_root.expanduser().resolve(strict=False)
    resolved_target = target.expanduser().resolve(strict=False)
    resolved_project = (
        project_root.expanduser().resolve(strict=False)
        if project_root is not None
        else resolved_root.parent
    )
    resolved_home = (home or Path.home()).expanduser().resolve(strict=False)
    filesystem_root = Path(resolved_target.anchor or "/").resolve(strict=False)

    if resolved_root in {filesystem_root, resolved_home, resolved_project}:
        raise UnsafePathError(f"Root dei laboratori generati non sicura: {resolved_root}")
    if not resolved_root.is_relative_to(resolved_project):
        raise UnsafePathError(
            "Root dei laboratori generati esterna al progetto: "
            f"{resolved_root} (progetto: {resolved_project})"
        )
    if resolved_target == resolved_root:
        raise UnsafePathError("È vietato cancellare kathara-lab-generates nella sua interezza")
    if not resolved_target.is_relative_to(resolved_root):
        raise UnsafePathError(
            f"Path distruttivo esterno a kathara-lab-generates: {resolved_target}"
        )

    for protected in (filesystem_root, resolved_project, resolved_home):
        if _is_same_or_ancestor(resolved_target, protected):
            raise UnsafePathError(f"Path distruttivo protetto: {resolved_target}")

    if target.is_symlink():
        raise UnsafePathError(f"Un symlink non può essere cancellato con rmtree: {target}")
    return resolved_target


def safe_rmtree(
    target: Path,
    generated_root: Path,
    *,
    project_root: Path | None = None,
    home: Path | None = None,
) -> None:
    """Remove one validated directory below the generated-labs root."""

    resolved_target = assert_safe_destructive_path(
        target,
        generated_root,
        project_root=project_root,
        home=home,
    )
    if not resolved_target.exists():
        return
    if not resolved_target.is_dir():
        raise UnsafePathError(f"Il target di rmtree non è una directory: {resolved_target}")
    try:
        shutil.rmtree(resolved_target)
    except OSError as exc:
        raise UnsafePathError(
            f"Impossibile cancellare in sicurezza {resolved_target}: {exc}"
        ) from exc


def build_job_paths(generated_root: Path, lab_id: str) -> JobPaths:
    """Build all canonical and ephemeral paths for one job."""

    safe_lab_id = sanitize_lab_id(lab_id)
    root = generated_root.expanduser().resolve(strict=False) / safe_lab_id
    checker_run = root / "checker-run"
    labs_dir = checker_run / "labs"
    correction_dir = root / "correction"
    workspaces = root / ".workspaces"
    return JobPaths(
        root=root,
        prompt=root / "prompt.md",
        source=root / "source",
        correction_dir=correction_dir,
        correction=correction_dir / "correction.yaml",
        checker_run=checker_run,
        labs_dir=labs_dir,
        candidate=labs_dir / "candidate",
        reports=root / "reports",
        logs=root / "logs",
        manifest=root / "manifest.json",
        lab_workspace=workspaces / "lab",
        correction_workspace=workspaces / "correction",
    )
