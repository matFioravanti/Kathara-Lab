from __future__ import annotations

import ipaddress
import os
import re
import stat
from pathlib import Path

from .models import ValidationResult

_DEVICE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_ASSIGNMENT_RE = re.compile(
    r'^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)\s*\[\s*([^\]]+)\s*\]\s*=\s*'
    r'(?:(?:"([^"]*)")|(?:\'([^\']*)\')|([^\s#]+))\s*(?:#.*)?$'
)
_ASSIGNMENT_PREFIX_RE = re.compile(r"^\s*[A-Za-z0-9][A-Za-z0-9_.-]*\s*\[")
_PLACEHOLDER_RE = re.compile(rb"(?i)(?<![A-Z0-9_])(TODO|CHANGE_ME|INSERT_HERE)(?![A-Z0-9_])")
_RESERVED_TOP_LEVEL_DIRS = {"shared", "images"}

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
        return bool(_PLACEHOLDER_RE.search(path.read_bytes()))
    except OSError:
        return False



def _parse_topology_text(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    topology: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = _ASSIGNMENT_RE.match(line)
        if not match:
            if _ASSIGNMENT_PREFIX_RE.match(line):
                errors.append(f"Malformed lab.conf assignment at line {lineno}: {stripped}")
            continue
        device, key = match.group(1), match.group(2).strip()
        value = next((part for part in match.groups()[2:] if part is not None), "")
        if not _DEVICE_RE.fullmatch(device):
            errors.append(f"Invalid device name at line {lineno}: {device}")
            continue
        signature = (device.casefold(), key.casefold())
        if signature in seen:
            errors.append(f"Duplicate lab.conf declaration at line {lineno}: {device}[{key}]")
            continue
        seen.add(signature)
        if key.isdigit():
            if not value.strip():
                errors.append(f"Empty collision domain at line {lineno}: {device}[{key}]")
            topology.setdefault(device, {})[key] = value
        else:
            topology.setdefault(device, {})
    if not topology:
        errors.append("lab.conf does not declare any device")
    if topology and not any(interfaces for interfaces in topology.values()):
        errors.append("lab.conf does not declare any numeric interface mapping")
    return topology, errors


def parse_lab_topology(lab_conf: Path) -> dict[str, dict[str, str]]:
    text = Path(lab_conf).read_text(encoding="utf-8")
    topology, errors = _parse_topology_text(text)
    if errors:
        raise ValueError("; ".join(errors))
    return topology


class LabValidator:
    """Static sanity validator; it never starts Kathara or judges runtime correctness."""

    def validate(self, lab_dir: Path, prompt_text: str = "") -> ValidationResult:
        lab_dir = Path(lab_dir)
        errors: list[str] = []
        if not lab_dir.exists():
            return ValidationResult(False, (f"Lab directory does not exist: {lab_dir}",))
        if not lab_dir.is_dir() or lab_dir.is_symlink():
            return ValidationResult(False, (f"Lab path is not a regular directory: {lab_dir}",))

        root = lab_dir.resolve()
        lab_conf = lab_dir / "lab.conf"
        text = ""
        if not lab_conf.exists():
            errors.append("Missing required lab.conf")
        elif lab_conf.is_symlink() or not lab_conf.is_file():
            errors.append("lab.conf must be a regular file, not a symlink")
        elif not _has_read_bits(lab_conf):
            errors.append("lab.conf is not readable")
        else:
            try:
                text = lab_conf.read_text(encoding="utf-8")
                if not text.strip():
                    errors.append("lab.conf is empty")
            except (OSError, UnicodeError) as exc:
                errors.append(f"Cannot read lab.conf as UTF-8: {exc}")

        all_files: list[Path] = []
        top_dirs: list[Path] = []
        for current, dir_names, file_names in os.walk(lab_dir, followlinks=False):
            current_path = Path(current)
            if current_path == lab_dir:
                top_dirs.extend(current_path / name for name in dir_names)
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
                    all_files.append(entry)
                    if not _has_read_bits(entry):
                        errors.append(f"Unreadable file: {entry.relative_to(lab_dir)}")
                    if _contains_placeholder(entry):
                        errors.append(f"Placeholder token found in: {entry.relative_to(lab_dir)}")
                elif not entry.is_dir():
                    errors.append(f"Non-regular filesystem entry: {entry.relative_to(lab_dir)}")

        nested = [p for p in all_files if p.name == "lab.conf" and p != lab_conf]
        for path in nested:
            errors.append(f"Nested lab.conf is not allowed: {path.relative_to(lab_dir)}")

        topology: dict[str, dict[str, str]] = {}
        if text.strip():
            topology, parse_errors = _parse_topology_text(text)
            errors.extend(parse_errors)
        devices = set(topology)

        startup_seen: set[str] = set()
        for startup in [p for p in all_files if p.parent == lab_dir and p.suffix.casefold() == ".startup"]:
            device = startup.stem
            folded = device.casefold()
            if folded in startup_seen:
                errors.append(f"Duplicate startup file for device: {device}")
            startup_seen.add(folded)
            if devices and device not in devices:
                errors.append(f"Startup file references undeclared device: {startup.name}")
            try:
                if not startup.read_text(encoding="utf-8").strip():
                    errors.append(f"Startup file is empty: {startup.name}")
            except (OSError, UnicodeError):
                pass

        for directory in top_dirs:
            if directory.is_symlink():
                continue
            name = directory.name
            if name.startswith(".") or name.casefold() in _RESERVED_TOP_LEVEL_DIRS:
                continue
            if devices and name not in devices:
                errors.append(f"Top-level device directory is not declared in lab.conf: {name}")


        return ValidationResult(not errors, tuple(errors), data={"topology": topology})
