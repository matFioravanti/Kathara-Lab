from __future__ import annotations

import ipaddress
import os
import re
import stat
from pathlib import Path

from .models import ValidationResult


_DEVICE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_ASSIGNMENT_RE = re.compile(
    r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)\s*\[\s*([^\]]+)\s*\]\s*=\s*"
    r"(?:\"([^\"]*)\"|'([^']*)'|([^\s#]+))\s*(?:#.*)?$"
)
_ASSIGNMENT_PREFIX_RE = re.compile(r"^\s*[A-Za-z0-9][A-Za-z0-9_.-]*\s*\[")
_PLACEHOLDER_RE = re.compile(rb"(?i)(?<![A-Z0-9_])(TODO|CHANGE_ME|INSERT_HERE)(?![A-Z0-9_])")
_REQUIRED_FILE_RE = re.compile(
    r"(?<![A-Za-z0-9_.:/-])(?:[`'\"])?"
    r"((?:/?[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\."
    r"(?:conf|cfg|startup|zone|html?|sh|json|ya?ml|txt))"
    r"(?:[`'\"])?(?![A-Za-z0-9_.-])",
    re.IGNORECASE,
)
_CONTEXTUAL_ARTIFACT_RE = re.compile(
    r"(?i)\b(?:file|path|percorso|artifact|documento)\s+"
    r"(?:(?:at|in|nel|nella|under|sotto)\s+)?"
    r"[`'\"]?((?:/?[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+)[`'\"]?"
)
_SPECIAL_ARTIFACT_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(db\.[A-Za-z0-9_.-]+|Dockerfile|Makefile)"
    r"(?![A-Za-z0-9_.-])",
    re.IGNORECASE,
)
_NAMED_ARTIFACT_RE = re.compile(
    r"(?i)\b(?:file|artifact|documento)\s+(?:named|called|chiamat[oa])\s+"
    r"([A-Za-z0-9_.-]+)\b|"
    r"\b(?:create|generate|crea|genera)\s+(?:the\s+|il\s+|un\s+)?"
    r"(?:file|artifact|documento)\s+(?:(?:named|called|chiamat[oa])\s+)?"
    r"([A-Za-z0-9_.-]+)\b"
)
_BACKTICK_TOKEN_RE = re.compile(r"`([^`\r\n]+)`")
_MULTICOMPONENT_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.:/-])"
    r"((?:/?[A-Za-z0-9_.-]+/){2,}[A-Za-z0-9_.-]+)"
    r"(?![A-Za-z0-9_.:/-])"
)
_ALL_STARTUPS_RE = re.compile(
    r"(?is)(?:\b(?:all|every|tutti|tutte|ogni)\b.{0,60}(?:device|devices|"
    r"dispositivo|dispositivi|router|host).{0,60}\.startup|"
    r"\.startup.{0,60}\b(?:all|every|tutti|tutte|ogni)\b)"
)

_IGNORED_REQUIRED_FILES = {
    "correction.yaml",
    "pipeline.yaml",
    "config-schema.json",
    "config-schema.yaml",
    "config-schema.yml",
    "manifest.json",
    "result-summary.json",
}
_NETWORK_NAME_SUFFIXES = {
    "com",
    "edu",
    "example",
    "int",
    "io",
    "it",
    "local",
    "net",
    "org",
    "test",
}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _parse_topology_text(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Parse device/interface declarations from lab.conf-compatible text.

    The public topology representation intentionally contains only numeric
    interfaces.  A device that has metadata but no interface is represented by
    an empty mapping.  Collision-domain values such as ``LAN/aa:bb:...`` are
    normalised to ``LAN`` because the suffix is a requested MAC address.
    """

    topology: dict[str, dict[str, str]] = {}
    seen_properties: set[tuple[str, str]] = set()
    errors: list[str] = []

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("LAB_"):
            continue

        match = _ASSIGNMENT_RE.match(raw_line)
        if match is None:
            if _ASSIGNMENT_PREFIX_RE.match(raw_line):
                errors.append(f"lab.conf line {line_number}: malformed device assignment")
            else:
                errors.append(f"lab.conf line {line_number}: unrecognised syntax")
            continue

        device, raw_property = match.group(1), match.group(2).strip()
        value = next(value for value in match.groups()[2:] if value is not None)
        prop = raw_property.strip("\"'")

        if not _DEVICE_RE.fullmatch(device):
            errors.append(f"lab.conf line {line_number}: invalid device name {device!r}")
            continue

        normalised_property = str(int(prop)) if prop.isdecimal() else prop
        property_key = (device, normalised_property)
        if property_key in seen_properties:
            errors.append(
                f"lab.conf line {line_number}: duplicate declaration for {device}[{prop}]"
            )
            continue
        seen_properties.add(property_key)
        topology.setdefault(device, {})

        if prop.isdecimal():
            collision_domain = value.split("/", 1)[0].strip()
            if not collision_domain:
                errors.append(
                    f"lab.conf line {line_number}: empty collision domain for {device}[{prop}]"
                )
            else:
                topology[device][normalised_property] = collision_domain

    return topology, errors


def parse_lab_topology(lab_conf_or_dir: Path) -> dict[str, dict[str, str]]:
    """Return ``device -> interface number -> collision domain`` for a lab.

    ``lab_conf_or_dir`` may point either to a lab directory or directly to its
    ``lab.conf``.  Malformed or duplicate declarations raise ``ValueError`` so
    callers cannot accidentally validate against a partially parsed topology.
    """

    path = Path(lab_conf_or_dir)
    lab_conf = path / "lab.conf" if path.is_dir() else path
    text = lab_conf.read_text(encoding="utf-8")
    topology, errors = _parse_topology_text(text)
    if errors:
        raise ValueError("; ".join(errors))
    return topology


def _has_read_bits(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return bool(mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)) and os.access(path, os.R_OK)


def _contains_placeholder(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            overlap = b""
            while chunk := stream.read(64 * 1024):
                data = overlap + chunk
                if _PLACEHOLDER_RE.search(data):
                    return True
                overlap = data[-32:]
    except OSError:
        return False
    return False


def _looks_like_network_reference(candidate: str) -> bool:
    try:
        ipaddress.ip_network(candidate, strict=False)
    except ValueError:
        pass
    else:
        return True

    first_component = candidate.split("/", 1)[0].casefold().rstrip(".")
    labels = first_component.split(".")
    return len(labels) >= 2 and (
        labels[0] == "www" or labels[-1] in _NETWORK_NAME_SUFFIXES
    )


def _extract_required_files(
    prompt_text: str,
    devices: set[str] | None = None,
) -> set[str]:
    required: set[str] = set()
    known_devices = {device.casefold() for device in (devices or set())}

    def add(raw_candidate: str, *, allow_hidden: bool = False) -> None:
        candidate = raw_candidate.replace("\\", "/")
        if any(marker in candidate for marker in ("<", ">", "*", "{")):
            return
        candidate = candidate.lstrip("/")
        if (
            not candidate
            or (Path(candidate).name.startswith(".") and not allow_hidden)
            or candidate.startswith(
                ("bin/", "sbin/", "usr/bin/", "usr/sbin/", "proc/", "sys/", "dev/")
            )
        ):
            return
        if Path(candidate).name.lower() in _IGNORED_REQUIRED_FILES:
            return
        required.add(candidate)

    def add_explicit(raw_candidate: str) -> None:
        candidate = raw_candidate.strip().replace("\\", "/")
        while candidate.startswith("./"):
            candidate = candidate[2:]
        candidate = candidate.lstrip("/")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", candidate):
            return
        if _looks_like_network_reference(candidate):
            return
        parts = Path(candidate).parts
        basename = Path(candidate).name
        if len(parts) > 1:
            strongly_file_like = (
                parts[0].casefold() in known_devices
                or len(parts) >= 3
                or "." in basename
                or basename.casefold() in {"dockerfile", "makefile"}
            )
            if not strongly_file_like:
                return
        elif not (
            basename.startswith(".")
            or "." in basename
            or basename.casefold() in {"dockerfile", "makefile"}
        ):
            return
        add(candidate, allow_hidden=True)

    for match in _REQUIRED_FILE_RE.finditer(prompt_text):
        add(match.group(1))
    for match in _CONTEXTUAL_ARTIFACT_RE.finditer(prompt_text):
        candidate = match.group(1)
        if "/" in candidate or "." in candidate or candidate.casefold() in {
            "dockerfile",
            "makefile",
        }:
            add(candidate, allow_hidden=True)
    for match in _SPECIAL_ARTIFACT_RE.finditer(prompt_text):
        add(match.group(1))
    for match in _NAMED_ARTIFACT_RE.finditer(prompt_text):
        candidate = match.group(1) or match.group(2)
        add(candidate, allow_hidden=True)
    for match in _BACKTICK_TOKEN_RE.finditer(prompt_text):
        add_explicit(match.group(1))
    for match in _MULTICOMPONENT_PATH_RE.finditer(prompt_text):
        add_explicit(match.group(1))
    nested_basenames = {
        Path(candidate).name.casefold()
        for candidate in required
        if len(Path(candidate).parts) > 1
    }
    return {
        candidate
        for candidate in required
        if len(Path(candidate).parts) > 1
        or candidate.casefold() not in nested_basenames
    }


def _required_file_exists(lab_dir: Path, candidate: str, all_files: list[Path]) -> bool:
    candidate_path = Path(candidate)
    if len(candidate_path.parts) > 1:
        suffix = candidate_path.as_posix().lower()
        return any(path.relative_to(lab_dir).as_posix().lower().endswith(suffix) for path in all_files)
    basename = candidate_path.name.lower()
    return any(path.name.lower() == basename for path in all_files)


class LabValidator:
    """Perform conservative, static checks on a generated Kathara lab."""

    def validate(self, lab_dir: Path, prompt_text: str = "") -> ValidationResult:
        lab_dir = Path(lab_dir)
        errors: list[str] = []

        if not lab_dir.exists():
            return ValidationResult(False, (f"Lab directory does not exist: {lab_dir}",), mode="static")
        if not lab_dir.is_dir():
            return ValidationResult(False, (f"Lab path is not a directory: {lab_dir}",), mode="static")

        root = lab_dir.resolve()
        lab_conf = lab_dir / "lab.conf"
        if not lab_conf.exists():
            errors.append("Missing required lab.conf")
        elif lab_conf.is_symlink():
            errors.append("lab.conf must be a regular file, not a symlink")
        elif not lab_conf.is_file():
            errors.append("lab.conf is not a regular file")
        elif not _has_read_bits(lab_conf):
            errors.append("lab.conf is not readable")

        all_files: list[Path] = []
        top_level_directories: list[Path] = []
        for current, dir_names, file_names in os.walk(lab_dir, followlinks=False):
            current_path = Path(current)
            if current_path == lab_dir:
                top_level_directories.extend(current_path / name for name in dir_names)

            if current_path != lab_dir and not dir_names and not file_names:
                errors.append(f"Empty directory: {current_path.relative_to(lab_dir)}")

            for name in [*dir_names, *file_names]:
                entry = current_path / name
                if entry.is_symlink():
                    try:
                        target = entry.resolve(strict=True)
                    except (OSError, RuntimeError):
                        errors.append(f"Broken or cyclic symlink: {entry.relative_to(lab_dir)}")
                        continue
                    if not _is_within(target, root):
                        errors.append(
                            f"Symlink escapes the lab directory: {entry.relative_to(lab_dir)} -> {target}"
                        )

            for name in file_names:
                path = current_path / name
                if path.is_symlink():
                    # Safe in-tree symlinks are allowed, but their target is not
                    # re-read here; it will be validated at its canonical entry.
                    continue
                if not path.is_file():
                    errors.append(f"Not a regular file: {path.relative_to(lab_dir)}")
                    continue
                all_files.append(path)
                if not _has_read_bits(path):
                    errors.append(f"Unreadable file: {path.relative_to(lab_dir)}")
                    continue
                if _contains_placeholder(path):
                    errors.append(f"Placeholder token found in {path.relative_to(lab_dir)}")

                if path.name == "lab.conf" and path != lab_conf:
                    errors.append(f"Nested lab.conf found at {path.relative_to(lab_dir)}")

        topology: dict[str, dict[str, str]] = {}
        if lab_conf.is_file() and not lab_conf.is_symlink() and _has_read_bits(lab_conf):
            try:
                text = lab_conf.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                errors.append(f"lab.conf is not valid UTF-8: {exc}")
            except OSError as exc:
                errors.append(f"Cannot read lab.conf: {exc}")
            else:
                if not text.strip():
                    errors.append("lab.conf is empty")
                topology, parse_errors = _parse_topology_text(text)
                errors.extend(parse_errors)
                if not topology:
                    errors.append("lab.conf declares no devices")

        devices = set(topology)
        startup_files = [path for path in all_files if path.parent == lab_dir and path.name.endswith(".startup")]
        startup_devices: set[str] = set()
        for startup in startup_files:
            device = startup.name[: -len(".startup")]
            if device in startup_devices:
                errors.append(f"Duplicate startup file for device {device}")
            startup_devices.add(device)
            if device not in devices:
                errors.append(f"Startup file references undeclared device: {startup.name}")
            try:
                if startup.stat().st_size == 0:
                    errors.append(f"Startup file is empty: {startup.name}")
            except OSError:
                pass

        for directory in top_level_directories:
            if directory.is_symlink():
                continue
            if directory.name != "shared" and directory.name not in devices:
                errors.append(f"Top-level device directory is not declared in lab.conf: {directory.name}")

        required_files = _extract_required_files(prompt_text, devices)
        if _ALL_STARTUPS_RE.search(prompt_text):
            required_files.update(f"{device}.startup" for device in devices)

        # Exact startup references are meaningful only for devices in this lab;
        # other textual filenames are searched recursively by suffix/basename.
        for required in sorted(required_files, key=str.casefold):
            if not _required_file_exists(lab_dir, required, all_files):
                errors.append(f"File explicitly required by prompt is missing: {required}")

        return ValidationResult(
            valid=not errors,
            errors=tuple(dict.fromkeys(errors)),
            mode="static",
            data={"topology": topology},
        )


__all__ = ["LabValidator", "parse_lab_topology"]
