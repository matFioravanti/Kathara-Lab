from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .models import ValidationResult

_ALLOWED_TOP = {"lab_inline", "structure", "convergence_time", "default_image", "test"}
_ALLOWED_TEST = {
    "requiring_startup", "ip_mapping", "daemons", "kernel_routes", "protocols",
    "applications", "reachability", "custom_commands",
}
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
            assertions = [key for key in ("regex_match", "output", "exit_code") if key in entry]
            if not assertions:
                errors.append(
                    f"custom_commands.{device}[{index}] requires at least one of regex_match, output, exit_code"
                )
            unknown = set(entry) - {"command", "regex_match", "output", "exit_code"}
            if unknown:
                errors.append(
                    f"custom_commands.{device}[{index}] has unsupported keys: {', '.join(sorted(unknown))}"
                )
            lower = (command or "").casefold() if isinstance(command, str) else ""
            destructive = (" rm ", "rm -", "shutdown", "reboot", "kill ", "pkill", "apt ", "apt-get", ">", "sed -i", "ip addr add", "ip route add")
            padded = f" {lower} "
            if any(token in padded for token in destructive):
                errors.append(f"custom_commands.{device}[{index}] uses a potentially destructive command")


def _validate_http(test: dict[str, Any], errors: list[str]) -> None:
    apps = test.get("applications")
    if apps is None:
        return
    if not isinstance(apps, dict):
        errors.append("test.applications must be a mapping")
        return
    http = apps.get("http")
    if http is None:
        return
    if not isinstance(http, dict):
        errors.append("test.applications.http must be a mapping")
        return
    for device, entries in http.items():
        if not isinstance(entries, list):
            errors.append(f"applications.http.{device} must be a list")
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"applications.http.{device}[{index}] must be a mapping")
                continue
            if "expected_status" in entry:
                errors.append(
                    f"applications.http.{device}[{index}] uses expected_status; checker 0.1.14 requires status_code"
                )
            if "status_code" not in entry:
                errors.append(f"applications.http.{device}[{index}] requires status_code")


def _validate_interface_keys(test: dict[str, Any], errors: list[str]) -> None:
    mapping = test.get("ip_mapping")
    if mapping is None:
        return
    if not isinstance(mapping, dict):
        errors.append("test.ip_mapping must be a mapping")
        return
    for device, interfaces in mapping.items():
        if not isinstance(interfaces, dict):
            errors.append(f"ip_mapping.{device} must be a mapping")
            continue
        for key, value in interfaces.items():
            if not isinstance(key, str) or not re.fullmatch(r"eth\d+", key):
                errors.append(f"ip_mapping.{device} interface key must use ethN for checker 0.1.14: {key!r}")
            if not isinstance(value, str) or "/" not in value:
                errors.append(f"ip_mapping.{device}.{key} must be an IP/prefix string")


def _validate_protocol_shape(test: dict[str, Any], errors: list[str]) -> None:
    protocols = test.get("protocols")
    if protocols is None:
        return
    if not isinstance(protocols, dict):
        errors.append("test.protocols must be a mapping")
        return
    allowed = {"bgpd", "ripd", "ospfd", "ospf6d"}
    for proto in protocols:
        if proto not in allowed:
            errors.append(f"Unsupported protocol block for checker 0.1.14: {proto}")
    ospf = protocols.get("ospfd")
    if isinstance(ospf, dict):
        routes = ospf.get("routes")
        if isinstance(routes, dict):
            for device, entries in routes.items():
                if isinstance(entries, list):
                    for index, entry in enumerate(entries):
                        if not isinstance(entry, dict) or "route" not in entry:
                            errors.append(f"protocols.ospfd.routes.{device}[{index}] must be an object containing route")
        interfaces = ospf.get("interfaces")
        if isinstance(interfaces, dict):
            for device, entries in interfaces.items():
                if isinstance(entries, list):
                    for index, entry in enumerate(entries):
                        if isinstance(entry, dict):
                            name = entry.get("name") or entry.get("interface")
                            if name is not None and (not isinstance(name, str) or not re.fullmatch(r"eth\d+", name)):
                                errors.append(f"protocols.ospfd.interfaces.{device}[{index}] must use ethN")
    # EVPN must live under bgpd in the verified 0.1.14 syntax.
    if "evpn" in protocols:
        errors.append("EVPN must be represented under protocols.bgpd for checker 0.1.14")


class CorrectionValidator:
    """Validate canonical correction syntax without inspecting a candidate lab."""

    def __init__(self, schema_path: Path | None = None):
        self.schema_path = Path(schema_path) if schema_path else None

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
        unknown = set(data) - _ALLOWED_TOP
        if unknown:
            errors.append("Unknown top-level keys: " + ", ".join(sorted(map(str, unknown))))
        if "labs_path" in data:
            errors.append("labs_path is forbidden in a canonical paired correction")
        if "lab_inline" not in data:
            errors.append("canonical correction must define lab_inline")
        elif not isinstance(data.get("lab_inline"), str) or not data["lab_inline"].strip():
            errors.append("lab_inline must be a non-empty string")
        if "structure" in data:
            errors.append("canonical correction must use lab_inline, not structure")
        convergence = data.get("convergence_time")
        if convergence is not None and (isinstance(convergence, bool) or not isinstance(convergence, int) or convergence < 0):
            errors.append("convergence_time must be a non-negative integer")
        test = data.get("test")
        if not isinstance(test, dict) or not test:
            errors.append("test must be a non-empty mapping")
        else:
            unknown_test = set(test) - _ALLOWED_TEST
            if unknown_test:
                errors.append("Unknown test keys: " + ", ".join(sorted(map(str, unknown_test))))
            _walk_custom_commands(test.get("custom_commands"), errors)
            _validate_http(test, errors)
            _validate_interface_keys(test, errors)
            _validate_protocol_shape(test, errors)
        return ValidationResult(not errors, tuple(errors), data=data)
