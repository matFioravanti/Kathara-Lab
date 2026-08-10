from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .models import ValidationResult

_PLACEHOLDER = re.compile(r"(?i)\b(?:TODO|CHANGE_ME|INSERT_HERE)\b")


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False):
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing mapping", node.start_mark,
                f"duplicate YAML key: {key!r}", key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def _walk_custom_commands(value: Any, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append("test.custom_commands must be a mapping")
        return
    for device, entries in value.items():
        if not isinstance(device, str) or not isinstance(entries, list):
            errors.append("test.custom_commands entries must map device names to lists")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"custom_commands.{device}[{index}] must be a mapping")
                continue
            command = entry.get("command")
            if not isinstance(command, str) or not command.strip():
                errors.append(f"custom_commands.{device}[{index}] requires command")
            lower = (command or "").casefold() if isinstance(command, str) else ""
            destructive = (" rm ", "rm -", "shutdown", "reboot", "kill ", "pkill", "apt ", "apt-get", ">", "sed -i", "ip addr add", "ip route add")
            padded = f" {lower} "
            if any(token in padded for token in destructive):
                errors.append(f"custom_commands.{device}[{index}] uses a potentially destructive command")


class CorrectionValidator:
    """Validate sanity of candidate-independent correction syntax without inspecting a candidate lab.
    Does not perform deep schema validation, which is delegated to the Kathara Lab Checker.
    """

    def __init__(self):
        pass

    def validate(self, correction: Path) -> ValidationResult:
        path = Path(correction)
        errors: list[str] = []
        if not path.is_file() or path.is_symlink():
            return ValidationResult(False, (f"Canonical correction not found: {path}",))
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return ValidationResult(False, (f"Cannot read correction as UTF-8: {exc}",))
        if not raw.strip():
            return ValidationResult(False, ("Canonical correction is empty",))
        if _PLACEHOLDER.search(raw):
            errors.append("correction contains placeholder token")
        try:
            data = yaml.load(raw, Loader=_UniqueKeyLoader)
        except yaml.YAMLError as exc:
            return ValidationResult(False, (f"Invalid YAML syntax: {exc}",))
        if not isinstance(data, dict):
            return ValidationResult(False, ("correction must be a top-level mapping",))
            
        if "lab_inline" not in data:
            errors.append("canonical correction must define lab_inline")
        elif not isinstance(data.get("lab_inline"), str) or not data["lab_inline"].strip():
            errors.append("lab_inline must be a non-empty string")
            
        test = data.get("test")
        if not isinstance(test, dict) or not test:
            errors.append("test must be a non-empty mapping")
        else:
            _walk_custom_commands(test.get("custom_commands"), errors)
            
        return ValidationResult(not errors, tuple(errors), data=data)
