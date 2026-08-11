from __future__ import annotations

import os
import re
import stat
from pathlib import Path

from .models import ValidationResult

# Matches obvious unresolved placeholders left by the generator
_PLACEHOLDER_RE = re.compile(rb"(?i)(?<![A-Z0-9_])(TODO|CHANGE_ME|INSERT_HERE)(?![A-Z0-9_])")
# Matches angle-bracket style placeholders like <device_name>, <ip_address>
_ANGLE_BRACKET_RE = re.compile(rb"<[^>]{1,64}>")


def _has_read_bits(path: Path) -> bool:
    try:
        return bool(path.stat().st_mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH))
    except OSError:
        return False


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _contains_placeholder(path: Path) -> bool:
    try:
        data = path.read_bytes()
        return bool(_PLACEHOLDER_RE.search(data) or _ANGLE_BRACKET_RE.search(data))
    except OSError:
        return False


class LabValidator:
    """Generic filesystem sanity validator.

    Checks only that the lab artefact is physically present, readable and not
    obviously incomplete or dangerous.  It does NOT interpret Kathara syntax,
    topology, routing, IP addresses, startup file requirements, or any other
    domain-specific semantics.  Correctness of the lab content is delegated to
    the subsequent runtime phase (kathara-lab-checker).
    """

    def validate(self, lab_dir: Path, prompt_text: str = "") -> ValidationResult:
        lab_dir = Path(lab_dir)
        errors: list[str] = []

        # --- directory exists and is a real directory ---
        if not lab_dir.exists():
            return ValidationResult(False, (f"Lab directory does not exist: {lab_dir}",))
        if not lab_dir.is_dir() or lab_dir.is_symlink():
            return ValidationResult(False, (f"Lab path is not a regular directory: {lab_dir}",))

        root = lab_dir.resolve()

        # --- lab.conf exists, is a regular file, is non-empty and readable ---
        lab_conf = lab_dir / "lab.conf"
        if not lab_conf.exists():
            errors.append("Missing required lab.conf")
        elif lab_conf.is_symlink() or not lab_conf.is_file():
            errors.append("lab.conf must be a regular file, not a symlink")
        elif not _has_read_bits(lab_conf):
            errors.append("lab.conf is not readable")
        else:
            try:
                text = lab_conf.read_bytes()
                if not text.strip():
                    errors.append("lab.conf is empty")
            except OSError as exc:
                errors.append(f"Cannot read lab.conf: {exc}")

        # --- walk the entire tree: check symlinks, readability, placeholders ---
        for current, dir_names, file_names in os.walk(lab_dir, followlinks=False):
            current_path = Path(current)
            for name in [*dir_names, *file_names]:
                entry = current_path / name
                if entry.is_symlink():
                    try:
                        target = entry.resolve(strict=True)
                    except (OSError, RuntimeError):
                        errors.append(f"Broken or cyclic symlink: {entry.relative_to(lab_dir)}")
                        continue
                    if not _is_within(target, root):
                        errors.append(f"Symlink escapes the lab directory: {entry.relative_to(lab_dir)}")
                    continue
                if entry.is_file():
                    if not _has_read_bits(entry):
                        errors.append(f"Unreadable file: {entry.relative_to(lab_dir)}")
                    if _contains_placeholder(entry):
                        errors.append(f"Placeholder token found in: {entry.relative_to(lab_dir)}")
                elif not entry.is_dir():
                    errors.append(f"Non-regular filesystem entry: {entry.relative_to(lab_dir)}")

        # --- nested lab.conf files are not allowed ---
        for current, _, file_names in os.walk(lab_dir, followlinks=False):
            current_path = Path(current)
            if current_path == lab_dir:
                continue
            for name in file_names:
                if name == "lab.conf":
                    errors.append(f"Nested lab.conf is not allowed: {(current_path / name).relative_to(lab_dir)}")

        return ValidationResult(not errors, tuple(errors))
