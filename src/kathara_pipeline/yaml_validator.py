from __future__ import annotations

import ipaddress
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

try:  # Preflight reports this dependency when a genuine JSON Schema is used.
    import jsonschema
except ImportError:  # pragma: no cover - exercised in minimal runtime environments
    jsonschema = None  # type: ignore[assignment]

from .lab_validator import _parse_topology_text, parse_lab_topology
from .models import ValidationResult


MAX_YAML_BYTES = 2 * 1024 * 1024
MAX_DATA_DEPTH = 80
MAX_DATA_NODES = 100_000

_PLACEHOLDER_RE = re.compile(r"(?i)(?<![A-Z0-9_])(TODO|CHANGE_ME|INSERT_HERE)(?![A-Z0-9_])")
_DEVICE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_DAEMON_RE = re.compile(r"^!?[A-Za-z0-9][A-Za-z0-9_.-]*$")
_HOST_RE = re.compile(
    r"^(?=.{1,253}\.?$)[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?"
    r"(?:\.[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?)*\.?$"
)
_INTERFACE_RE = re.compile(r"^(?:[0-9]+|eth[0-9]+|[A-Za-z][A-Za-z0-9_.:-]*)$")
_METHOD_RE = re.compile(r"^[A-Z]+$")
_SAFE_COMMAND_DESTINATION_RE = re.compile(r"^[A-Za-z0-9_.:%-]+$")
_IP_ASSIGNMENT_RE = re.compile(
    r"\bip(?:\s+-[46])?\s+(?:address|addr)\s+(?:add|replace)\s+"
    r"([^\s;]+).*?\bdev\s+([A-Za-z0-9_.:-]+)",
    re.IGNORECASE,
)
_IFCONFIG_ASSIGNMENT_RE = re.compile(
    r"\bifconfig\s+([A-Za-z0-9_.:-]+)\s+(?:add\s+|inet\s+)?"
    r"([^\s;]+)(?:\s+netmask\s+([^\s;]+))?",
    re.IGNORECASE,
)
_INLINE_PROPERTY_RE = re.compile(
    r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)\s*\[\s*([^\]]+)\s*\]\s*="
)

_TOP_LEVEL_KEYS = {
    "lab_inline",
    "labs_path",
    "convergence_time",
    "structure",
    "default_image",
    "test",
}
_TEST_KEYS = {
    "requiring_startup",
    "ip_mapping",
    "daemons",
    "kernel_routes",
    "protocols",
    "applications",
    "reachability",
    "custom_commands",
}
_PROTOCOLS = {"bgpd", "ripd", "ospfd", "ospf6d", "isisd", "babeld"}
_GENERIC_PROTOCOL_KEYS = {"networks", "injections"}
_PROTOCOL_KEYS = {
    "bgpd": _GENERIC_PROTOCOL_KEYS | {"neighbors", "routes", "evpn_sessions", "vtep_devices"},
    "ripd": _GENERIC_PROTOCOL_KEYS,
    "ospfd": _GENERIC_PROTOCOL_KEYS | {"neighbors", "routes", "interfaces"},
    "ospf6d": _GENERIC_PROTOCOL_KEYS,
    "isisd": _GENERIC_PROTOCOL_KEYS,
    "babeld": _GENERIC_PROTOCOL_KEYS,
}
_APPLICATION_KEYS = {"dns", "http"}
_DNS_KEYS = {"authoritative", "local_ns", "records"}
_HTTP_KEYS = {"url", "method", "status_code", "regex_body", "body_contains"}
_CUSTOM_KEYS = {"command", "regex_match", "output", "exit_code"}


@dataclass(slots=True)
class _DocumentedFields:
    top: set[str] = field(default_factory=set)
    test: set[str] = field(default_factory=set)
    protocols: set[str] = field(default_factory=set)
    protocol_keys: dict[str, set[str]] = field(default_factory=dict)
    applications: set[str] = field(default_factory=set)
    dns: set[str] = field(default_factory=set)
    http: set[str] = field(default_factory=set)
    custom: set[str] = field(default_factory=set)
    bgp_neighbors: set[str] = field(default_factory=set)
    bgp_routes: set[str] = field(default_factory=set)
    ospf_neighbors: set[str] = field(default_factory=set)
    ospf_routes: set[str] = field(default_factory=set)
    vtep_devices: set[str] = field(default_factory=set)


def _string_keys(value: Any) -> set[str]:
    return (
        {key for key in value if isinstance(key, str) and key != "..."}
        if isinstance(value, dict)
        else set()
    )


def _list_entry_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if not isinstance(value, dict):
        return keys
    for entries in value.values():
        if isinstance(entries, list):
            for entry in entries:
                keys.update(_string_keys(entry))
    return keys


def _collect_markdown_fields(raw: str) -> _DocumentedFields:
    """Derive the structural whitelist from YAML examples in the Markdown schema."""

    fields = _DocumentedFields()
    inline_identifiers = set(
        re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", raw)
    )
    fields.top.update(inline_identifiers.intersection(_TOP_LEVEL_KEYS))
    blocks = re.findall(r"```ya?ml\s*\n(.*?)```", raw, flags=re.IGNORECASE | re.DOTALL)
    for block in blocks:
        try:
            document = yaml.safe_load(block)
        except (yaml.YAMLError, RecursionError):
            continue
        if not isinstance(document, dict):
            continue
        fields.top.update(_string_keys(document))
        test = document.get("test")
        if not isinstance(test, dict):
            continue
        fields.test.update(_string_keys(test))

        protocols = test.get("protocols")
        if isinstance(protocols, dict):
            fields.protocols.update(_string_keys(protocols))
            for protocol, config in protocols.items():
                if isinstance(protocol, str) and isinstance(config, dict):
                    fields.protocol_keys.setdefault(protocol, set()).update(_string_keys(config))
                    if protocol == "bgpd":
                        fields.bgp_neighbors.update(
                            _list_entry_keys(config.get("neighbors"))
                        )
                        fields.bgp_routes.update(_list_entry_keys(config.get("routes")))
                    elif protocol == "ospfd":
                        fields.ospf_neighbors.update(
                            _list_entry_keys(config.get("neighbors"))
                        )
                        fields.ospf_routes.update(_list_entry_keys(config.get("routes")))

        applications = test.get("applications")
        if isinstance(applications, dict):
            fields.applications.update(_string_keys(applications))
            dns = applications.get("dns")
            if isinstance(dns, dict):
                fields.dns.update(_string_keys(dns))
            http = applications.get("http")
            if isinstance(http, dict):
                for checks in http.values():
                    if isinstance(checks, list):
                        for check in checks:
                            fields.http.update(_string_keys(check))

        custom = test.get("custom_commands")
        if isinstance(custom, dict):
            for commands in custom.values():
                if isinstance(commands, list):
                    for command in commands:
                        fields.custom.update(_string_keys(command))

    # Runtime 0.1.14 overrides for documented concepts whose Markdown examples
    # use an incompatible spelling or nesting.
    if "expected_status" in fields.http:
        fields.http.remove("expected_status")
        fields.http.add("status_code")
    if "ospfd" in fields.protocols:
        fields.protocol_keys.setdefault("ospfd", set()).update(
            {"neighbors", "routes", "interfaces"}
        )
        fields.ospf_neighbors = {"router_id", "state"}
        fields.ospf_routes = {"route"}
    if "evpn" in fields.protocols:
        fields.protocols.remove("evpn")
        fields.protocols.add("bgpd")
        fields.protocol_keys.pop("evpn", None)
        fields.protocol_keys.setdefault("bgpd", set()).update(
            {"evpn_sessions", "vtep_devices"}
        )
        fields.vtep_devices = {"ip", "vnis"}
    return fields


def _merge_skill_fields(
    fields: _DocumentedFields,
    skill_path: Path | None,
    errors: list[str],
) -> None:
    """Merge checker concepts explicitly documented by the companion Skill."""

    if skill_path is None:
        return
    if not skill_path.is_file() or skill_path.is_symlink():
        errors.append(f"Skill resource does not exist or is not a regular file: {skill_path}")
        return
    try:
        raw = skill_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read Skill resource {skill_path}: {exc}")
        return

    documents_generic_injections = bool(
        re.search(
            r"protocols\.(?:<proto>|\*|<ripd\|ospfd>)\.injections",
            raw,
            flags=re.IGNORECASE,
        )
    )
    if documents_generic_injections:
        for protocol in fields.protocols:
            if "injections" in _PROTOCOL_KEYS.get(protocol, set()):
                fields.protocol_keys.setdefault(protocol, set()).add("injections")


def _documented_support_errors(fields: _DocumentedFields) -> list[str]:
    unsupported: list[str] = []

    def collect(prefix: str, documented: set[str], supported: set[str]) -> None:
        unsupported.extend(f"{prefix}.{key}" for key in sorted(documented - supported))

    collect("$", fields.top, _TOP_LEVEL_KEYS)
    collect("$.test", fields.test, _TEST_KEYS)
    collect("$.test.protocols", fields.protocols, _PROTOCOLS)
    for protocol, keys in sorted(fields.protocol_keys.items()):
        collect(
            f"$.test.protocols.{protocol}",
            keys,
            _PROTOCOL_KEYS.get(protocol, set()),
        )
    collect("$.test.applications", fields.applications, _APPLICATION_KEYS)
    collect("$.test.applications.dns", fields.dns, _DNS_KEYS)
    collect("$.test.applications.http[*]", fields.http, _HTTP_KEYS)
    collect("$.test.custom_commands[*]", fields.custom, _CUSTOM_KEYS)
    collect("$.test.protocols.bgpd.neighbors[*]", fields.bgp_neighbors, {"ip", "asn"})
    collect("$.test.protocols.bgpd.routes[*]", fields.bgp_routes, {"route", "aspath"})
    collect(
        "$.test.protocols.ospfd.neighbors[*]",
        fields.ospf_neighbors,
        {"router_id", "state"},
    )
    collect("$.test.protocols.ospfd.routes[*]", fields.ospf_routes, {"route"})
    collect("$.test.protocols.bgpd.vtep_devices[*]", fields.vtep_devices, {"ip", "vnis"})
    if not unsupported:
        return []
    return [
        "Documented schema fields are not supported by this pipeline version: "
        + ", ".join(unsupported)
    ]


def _is_mapping(value: Any) -> bool:
    return isinstance(value, dict)


def _is_list(value: Any) -> bool:
    return isinstance(value, list)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _display_path(parts: Sequence[Any]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", str(part)):
            result += f".{part}"
        else:
            result += f"[{part!r}]"
    return result


def _short_repr(value: Any, limit: int = 160) -> str:
    representation = repr(value)
    return representation if len(representation) <= limit else representation[: limit - 3] + "..."


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _unknown_keys(value: Mapping[Any, Any], allowed: set[str], path: str, errors: list[str]) -> None:
    for key in value:
        if not isinstance(key, str):
            errors.append(f"{path}: mapping key must be a string, got {_short_repr(key)}")
        elif key not in allowed:
            errors.append(f"{path}: unknown key {key!r}")


def _mapping(value: Any, path: str, errors: list[str]) -> dict[Any, Any] | None:
    if not _is_mapping(value):
        errors.append(f"{path}: expected a mapping, got {type(value).__name__}")
        return None
    return value


def _list(value: Any, path: str, errors: list[str]) -> list[Any] | None:
    if not _is_list(value):
        errors.append(f"{path}: expected a list, got {type(value).__name__}")
        return None
    return value


def _string(value: Any, path: str, errors: list[str], *, nonempty: bool = True) -> str | None:
    if not isinstance(value, str):
        errors.append(f"{path}: expected a string, got {type(value).__name__}")
        return None
    if nonempty and not value.strip():
        errors.append(f"{path}: string must not be empty")
        return None
    return value


def _normalise_interface(interface: str) -> str:
    if interface.startswith("eth") and interface[3:].isdecimal():
        return str(int(interface[3:]))
    if interface.isdecimal():
        return str(int(interface))
    return interface


def _is_canonical_interface_reference(interface: str) -> bool:
    numeric = interface[3:] if interface.startswith("eth") else interface
    if not numeric.isdecimal():
        return True
    return numeric == "0" or not numeric.startswith("0")


def _raw_ip_literals(value: Any) -> set[str]:
    """Mirror the raw CIDR stripping used by checker 0.1.14 DNS lookup."""

    literals: set[str] = set()
    if not isinstance(value, dict):
        return literals
    for interfaces in value.values():
        if not isinstance(interfaces, dict):
            continue
        for address in interfaces.values():
            if isinstance(address, str):
                literals.add(address.split("/", 1)[0])
    return literals


def _duplicate_yaml_keys(raw: str) -> list[str]:
    errors: list[str] = []
    try:
        root = yaml.compose(raw, Loader=yaml.SafeLoader)
    except (yaml.YAMLError, RecursionError):
        return errors  # safe_load reports the useful syntax error

    active: set[int] = set()

    def visit(node: Node | None, parts: tuple[Any, ...]) -> None:
        if node is None:
            return
        node_id = id(node)
        if node_id in active:
            return
        active.add(node_id)
        try:
            if isinstance(node, MappingNode):
                seen: set[tuple[str, str]] = set()
                for key_node, value_node in node.value:
                    if isinstance(key_node, ScalarNode):
                        identity = (key_node.tag, key_node.value)
                        display = key_node.value
                    else:
                        identity = (key_node.tag, repr(key_node.value))
                        display = "<non-scalar key>"
                    if identity in seen:
                        errors.append(f"{_display_path(parts)}: duplicate YAML key {display!r}")
                    seen.add(identity)
                    visit(value_node, parts + (display,))
            elif isinstance(node, SequenceNode):
                for index, child in enumerate(node.value):
                    visit(child, parts + (index,))
        finally:
            active.remove(node_id)

    visit(root, ())
    return errors


def _yaml_comment_lines(raw: str) -> list[int]:
    """Find YAML comments while ignoring literal/folded scalar content."""

    comments: list[int] = []
    block_indent: int | None = None
    for line_number, line in enumerate(raw.splitlines(), 1):
        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)
        if block_indent is not None:
            if not stripped or indent > block_indent:
                continue
            block_indent = None

        single_quoted = False
        double_quoted = False
        escaped = False
        comment_index: int | None = None
        for index, character in enumerate(line):
            if escaped:
                escaped = False
                continue
            if character == "\\" and double_quoted:
                escaped = True
                continue
            if character == "'" and not double_quoted:
                single_quoted = not single_quoted
                continue
            if character == '"' and not single_quoted:
                double_quoted = not double_quoted
                continue
            if (
                character == "#"
                and not single_quoted
                and not double_quoted
                and (index == 0 or line[index - 1].isspace())
            ):
                comment_index = index
                comments.append(line_number)
                break

        content = line if comment_index is None else line[:comment_index]
        if re.search(r":\s*[>|][+-]?[0-9]?\s*$", content):
            block_indent = indent
    return comments


def _check_data_graph(data: Any) -> list[str]:
    """Reject recursive aliases and unreasonable post-load structures."""

    errors: list[str] = []
    active: set[int] = set()
    node_count = 0

    def visit(value: Any, depth: int, path: str) -> None:
        nonlocal node_count
        node_count += 1
        if node_count > MAX_DATA_NODES:
            if not any("too many nodes" in error for error in errors):
                errors.append(f"{path}: YAML expands to too many nodes")
            return
        if depth > MAX_DATA_DEPTH:
            if not any("maximum nesting depth" in error for error in errors):
                errors.append(f"{path}: YAML exceeds maximum nesting depth {MAX_DATA_DEPTH}")
            return

        if isinstance(value, (dict, list)):
            object_id = id(value)
            if object_id in active:
                errors.append(f"{path}: recursive YAML alias is not allowed")
                return
            active.add(object_id)
            try:
                if isinstance(value, dict):
                    for key, child in value.items():
                        visit(child, depth + 1, f"{path}.{key}")
                else:
                    for index, child in enumerate(value):
                        visit(child, depth + 1, f"{path}[{index}]")
            finally:
                active.remove(object_id)
        elif not isinstance(value, (str, int, float, bool, type(None))):
            errors.append(f"{path}: unsupported YAML value type {type(value).__name__}")

    visit(data, 0, "$")
    return errors


def _placeholder_errors(data: Any) -> list[str]:
    errors: list[str] = []
    visited: set[int] = set()

    def visit(value: Any, path: str) -> None:
        if isinstance(value, (dict, list)):
            object_id = id(value)
            if object_id in visited:
                return
            visited.add(object_id)
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(key, str) and _PLACEHOLDER_RE.search(key):
                    errors.append(f"{path}: placeholder token in key {key!r}")
                visit(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")
        elif isinstance(value, str) and _PLACEHOLDER_RE.search(value):
            errors.append(f"{path}: placeholder token found")

    visit(data, "$")
    return errors


def _schema_document(
    path: Path,
    skill_path: Path | None = None,
) -> tuple[str, dict[str, Any] | None, _DocumentedFields | None, list[str]]:
    errors: list[str] = []
    if not path.exists() or not path.is_file():
        return "documented-structural", None, None, [
            f"Schema resource does not exist or is not a file: {path}"
        ]
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return "documented-structural", None, None, [
            f"Cannot read schema resource {path}: {exc}"
        ]

    if path.suffix.lower() == ".md":
        documented = _collect_markdown_fields(raw)
        _merge_skill_fields(documented, skill_path, errors)
        if "test" not in documented.top or not documented.test:
            errors.append(
                "Markdown schema contains no usable top-level/test field definitions"
            )
        errors.extend(_documented_support_errors(documented))
        return "documented-structural", None, documented, errors

    try:
        candidate = json.loads(raw)
    except (json.JSONDecodeError, UnicodeError):
        try:
            candidate = yaml.safe_load(raw)
        except yaml.YAMLError:
            candidate = None

    schema_type = candidate.get("type") if isinstance(candidate, dict) else None
    genuine = isinstance(candidate, dict) and (
        "$schema" in candidate
        or (
            (schema_type == "object" or schema_type == ["object"])
            and isinstance(candidate.get("properties"), dict)
        )
    )
    if genuine:
        return "json-schema", candidate, None, errors
    documented = _collect_markdown_fields(f"```yaml\n{raw}\n```")
    _merge_skill_fields(documented, skill_path, errors)
    if "test" not in documented.top or not documented.test:
        errors.append("Structural schema contains no usable top-level/test field definitions")
    errors.extend(_documented_support_errors(documented))
    return "documented-structural", None, documented, errors


def _json_schema_errors(schema: dict[str, Any], data: dict[str, Any]) -> list[str]:
    if jsonschema is None:
        return ["jsonschema is required to validate the discovered JSON Schema"]
    try:
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        validator = validator_class(schema, format_checker=jsonschema.FormatChecker())
    except (jsonschema.SchemaError, TypeError, ValueError) as exc:
        return [f"Invalid JSON Schema: {exc}"]

    errors: list[str] = []
    for issue in sorted(validator.iter_errors(data), key=lambda item: tuple(str(part) for part in item.path)):
        path = _display_path(tuple(issue.path))
        errors.append(
            f"{path}: value {_short_repr(issue.instance)} violates {issue.validator!r}: {issue.message}"
        )
    return errors


def schema_support_errors(path: Path, skill_path: Path | None = None) -> tuple[str, ...]:
    """Return resource/capability errors suitable for blocking preflight."""

    _mode, _schema, _documented, errors = _schema_document(
        Path(path), Path(skill_path) if skill_path is not None else None
    )
    return tuple(errors)


def _startup_addresses(lab_dir: Path, device: str) -> dict[str, set[str]]:
    path = lab_dir / f"{device}.startup"
    addresses: dict[str, set[str]] = {}
    if not path.is_file():
        return addresses
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return addresses
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split("#", 1)[0]
        ip_match = _IP_ASSIGNMENT_RE.search(line)
        if ip_match is not None:
            raw_address, interface = ip_match.group(1).strip("'\""), ip_match.group(2)
            try:
                address = str(ipaddress.ip_interface(raw_address))
            except ValueError:
                pass
            else:
                addresses.setdefault(_normalise_interface(interface), set()).add(address)

        ifconfig_match = _IFCONFIG_ASSIGNMENT_RE.search(line)
        if ifconfig_match is None:
            continue
        interface, raw_address, raw_netmask = ifconfig_match.groups()
        raw_address = raw_address.strip("'\"")
        try:
            if "/" in raw_address:
                address = str(ipaddress.ip_interface(raw_address))
            elif raw_netmask:
                prefix = ipaddress.IPv4Network(f"0.0.0.0/{raw_netmask}").prefixlen
                address = str(ipaddress.ip_interface(f"{raw_address}/{prefix}"))
            else:
                # With no prefix/netmask, ifconfig's classful inference is
                # platform-dependent and is not safe to second-guess.
                continue
        except ValueError:
            continue
        addresses.setdefault(_normalise_interface(interface), set()).add(address)
    return addresses


class YamlValidator:
    """Validate correction YAML at syntax, schema, and lab-semantic levels."""

    def __init__(self, schema_path: Path, skill_path: Path | None = None) -> None:
        self.schema_path = Path(schema_path)
        self.skill_path = Path(skill_path) if skill_path is not None else None
        self._documented_keys = True
        self._top_keys = set(_TOP_LEVEL_KEYS)
        self._test_keys = set(_TEST_KEYS)
        self._protocols = set(_PROTOCOLS)
        self._protocol_keys = {
            protocol: set(keys) for protocol, keys in _PROTOCOL_KEYS.items()
        }
        self._application_keys = set(_APPLICATION_KEYS)
        self._dns_keys = set(_DNS_KEYS)
        self._http_keys = set(_HTTP_KEYS)
        self._custom_keys = set(_CUSTOM_KEYS)
        self._bgp_neighbor_keys = {"ip", "asn"}
        self._bgp_route_keys = {"route", "aspath"}
        self._ospf_neighbor_keys = {"router_id", "state"}
        self._ospf_route_keys = {"route"}
        self._vtep_device_keys = {"ip", "vnis"}

    def validate(self, correction_path: Path, lab_dir: Path, job_dir: Path) -> ValidationResult:
        correction_path = Path(correction_path)
        lab_dir = Path(lab_dir)
        job_dir = Path(job_dir)
        errors: list[str] = []
        mode, schema, documented, schema_resource_errors = _schema_document(
            self.schema_path, self.skill_path
        )
        self._documented_keys = schema is None
        if documented is not None:
            self._top_keys = documented.top
            self._test_keys = documented.test
            self._protocols = documented.protocols
            self._protocol_keys = documented.protocol_keys
            self._application_keys = documented.applications
            self._dns_keys = documented.dns
            self._http_keys = documented.http
            self._custom_keys = documented.custom
            self._bgp_neighbor_keys = documented.bgp_neighbors
            self._bgp_route_keys = documented.bgp_routes
            self._ospf_neighbor_keys = documented.ospf_neighbors
            self._ospf_route_keys = documented.ospf_routes
            self._vtep_device_keys = documented.vtep_devices
        errors.extend(schema_resource_errors)

        if not correction_path.exists() or not correction_path.is_file():
            errors.append(f"Correction file does not exist or is not a file: {correction_path}")
            return ValidationResult(False, tuple(errors), mode=mode)
        try:
            raw_bytes = correction_path.read_bytes()
        except OSError as exc:
            errors.append(f"Cannot read correction file: {exc}")
            return ValidationResult(False, tuple(errors), mode=mode)
        if len(raw_bytes) > MAX_YAML_BYTES:
            errors.append(
                f"Correction YAML is too large: {len(raw_bytes)} bytes (limit {MAX_YAML_BYTES})"
            )
            return ValidationResult(False, tuple(errors), mode=mode)
        try:
            raw = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"Correction YAML is not valid UTF-8: {exc}")
            return ValidationResult(False, tuple(errors), mode=mode)

        try:
            data = yaml.safe_load(raw)
        except (yaml.YAMLError, RecursionError) as exc:
            errors.append(f"Invalid YAML syntax: {exc}")
            return ValidationResult(False, tuple(errors), mode=mode)

        if not isinstance(data, dict):
            errors.append(f"Correction YAML must contain one top-level mapping, got {type(data).__name__}")
            return ValidationResult(False, tuple(errors), mode=mode)

        errors.extend(_duplicate_yaml_keys(raw))
        comment_lines = _yaml_comment_lines(raw)
        if comment_lines:
            errors.append(
                "Correction YAML must not contain comments; lines: "
                + ", ".join(str(line) for line in comment_lines)
            )
        graph_errors = _check_data_graph(data)
        errors.extend(graph_errors)
        if graph_errors:
            return ValidationResult(False, tuple(dict.fromkeys(errors)), mode=mode, data=data)
        errors.extend(_placeholder_errors(data))

        try:
            job_root = job_dir.resolve(strict=True)
        except OSError as exc:
            errors.append(f"Job directory is unavailable: {exc}")
            job_root = job_dir.resolve(strict=False)
        for label, path in (("correction", correction_path), ("lab", lab_dir)):
            try:
                resolved = path.resolve(strict=True)
            except OSError as exc:
                errors.append(f"{label.capitalize()} path is unavailable: {exc}")
                continue
            if not _is_within(resolved, job_root):
                errors.append(f"{label.capitalize()} path escapes the job directory: {resolved}")

        if schema is not None:
            errors.extend(_json_schema_errors(schema, data))

        try:
            topology = parse_lab_topology(lab_dir)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"Cannot parse lab topology: {exc}")
            topology = {}

        self._validate_document(data, correction_path, lab_dir, job_root, topology, errors)

        return ValidationResult(
            valid=not errors,
            errors=tuple(dict.fromkeys(errors)),
            mode=mode,
            data=data,
        )

    def _validate_keys(
        self,
        value: Mapping[Any, Any],
        allowed: set[str],
        path: str,
        errors: list[str],
    ) -> None:
        if self._documented_keys:
            _unknown_keys(value, allowed, path, errors)

    def _validate_document(
        self,
        data: dict[str, Any],
        correction_path: Path,
        lab_dir: Path,
        job_root: Path,
        topology: dict[str, dict[str, str]],
        errors: list[str],
    ) -> None:
        self._validate_keys(data, self._top_keys, "$", errors)

        convergence = data.get("convergence_time")
        if convergence is None and not self._documented_keys:
            pass
        elif not _is_int(convergence) or convergence < 0:
            errors.append("$.convergence_time: expected a non-negative integer")
        if "default_image" in data or self._documented_keys:
            _string(data.get("default_image"), "$.default_image", errors)

        inline = data.get("lab_inline")
        structure = data.get("structure")
        has_inline = isinstance(inline, str) and bool(inline.strip())
        has_structure = isinstance(structure, str) and bool(structure.strip())
        if (has_inline and has_structure) or (
            self._documented_keys and not has_inline and not has_structure
        ):
            errors.append("$: exactly one of non-empty lab_inline or structure is required")
        if "lab_inline" in data and not has_inline:
            errors.append("$.lab_inline: expected a non-empty string")
        if "structure" in data and not has_structure:
            errors.append("$.structure: expected a non-empty string")

        if has_inline:
            self._validate_inline_topology(inline, topology, errors)
        if has_structure:
            self._validate_structure_path(
                structure, correction_path.parent, job_root, topology, "$.structure", errors
            )
        if "labs_path" in data:
            labs_path = _string(data["labs_path"], "$.labs_path", errors)
            if labs_path is not None:
                self._validate_relative_path(labs_path, correction_path.parent, job_root, "$.labs_path", errors)

        if "test" not in data and not self._documented_keys:
            return
        test = _mapping(data.get("test"), "$.test", errors)
        if test is None:
            return
        self._validate_keys(test, self._test_keys, "$.test", errors)

        devices = set(topology)
        ip_mapping = self._validate_ip_mapping(test.get("ip_mapping"), topology, lab_dir, errors)
        self._validate_requiring_startup(test.get("requiring_startup"), devices, lab_dir, errors)
        self._validate_daemons(test.get("daemons"), devices, errors)
        self._validate_kernel_routes(test.get("kernel_routes"), topology, ip_mapping, errors)
        self._validate_reachability(test.get("reachability"), devices, ip_mapping, errors)
        self._validate_custom_commands(test.get("custom_commands"), devices, errors)
        self._validate_protocols(test.get("protocols"), devices, topology, errors)
        self._validate_applications(
            test.get("applications"),
            devices,
            ip_mapping,
            test.get("ip_mapping"),
            errors,
        )

    def _validate_relative_path(
        self,
        raw_path: str,
        base: Path,
        job_root: Path,
        path: str,
        errors: list[str],
        *,
        require_file: bool = False,
    ) -> Path | None:
        candidate = Path(raw_path)
        if candidate.is_absolute():
            errors.append(f"{path}: absolute paths are not allowed")
            return None
        resolved = (base / candidate).resolve(strict=False)
        if not _is_within(resolved, job_root):
            errors.append(f"{path}: path escapes the job directory")
            return None
        if require_file and (not resolved.exists() or not resolved.is_file()):
            errors.append(f"{path}: referenced file does not exist: {raw_path}")
            return None
        return resolved

    def _validate_structure_path(
        self,
        raw_path: str,
        base: Path,
        job_root: Path,
        topology: dict[str, dict[str, str]],
        path: str,
        errors: list[str],
    ) -> None:
        resolved = self._validate_relative_path(
            raw_path, base, job_root, path, errors, require_file=True
        )
        if resolved is None:
            return
        try:
            expected = parse_lab_topology(resolved)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{path}: invalid topology file: {exc}")
            return
        self._compare_topologies(expected, topology, path, errors)

    def _validate_inline_topology(
        self,
        inline: str,
        topology: dict[str, dict[str, str]],
        errors: list[str],
    ) -> None:
        for line_number, line in enumerate(inline.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            property_match = _INLINE_PROPERTY_RE.match(line)
            if property_match is None:
                errors.append(f"$.lab_inline line {line_number}: malformed topology declaration")
                continue
            prop = property_match.group(2).strip().strip("\"'")
            if not prop.isdecimal():
                errors.append(
                    f"$.lab_inline line {line_number}: only numeric interface mappings are allowed, got {prop!r}"
                )
        expected, parse_errors = _parse_topology_text(inline)
        errors.extend(f"$.lab_inline: {error}" for error in parse_errors)
        if not expected:
            errors.append("$.lab_inline: topology declares no devices")
            return
        self._compare_topologies(expected, topology, "$.lab_inline", errors)

    @staticmethod
    def _compare_topologies(
        expected: dict[str, dict[str, str]],
        actual: dict[str, dict[str, str]],
        path: str,
        errors: list[str],
    ) -> None:
        expected_devices, actual_devices = set(expected), set(actual)
        for device in sorted(expected_devices - actual_devices):
            errors.append(f"{path}: device {device!r} does not exist in current lab")
        for device in sorted(actual_devices - expected_devices):
            # A metadata-only/bridged device has no collision-domain mapping
            # that can legally be represented in topology-only lab_inline.
            if actual[device]:
                errors.append(f"{path}: current lab device {device!r} is missing from expected topology")
        for device in sorted(expected_devices & actual_devices):
            expected_ifaces, actual_ifaces = expected[device], actual[device]
            for interface in sorted(set(expected_ifaces) - set(actual_ifaces)):
                errors.append(f"{path}: interface {device}[{interface}] does not exist in current lab")
            for interface in sorted(set(actual_ifaces) - set(expected_ifaces)):
                errors.append(f"{path}: current interface {device}[{interface}] is missing")
            for interface in sorted(set(expected_ifaces) & set(actual_ifaces)):
                if expected_ifaces[interface] != actual_ifaces[interface]:
                    errors.append(
                        f"{path}: {device}[{interface}] uses collision domain "
                        f"{expected_ifaces[interface]!r}, current lab uses {actual_ifaces[interface]!r}"
                    )

    @staticmethod
    def _device(device: Any, devices: set[str], path: str, errors: list[str]) -> str | None:
        if not isinstance(device, str) or not _DEVICE_RE.fullmatch(device):
            errors.append(f"{path}: invalid device name {_short_repr(device)}")
            return None
        if device not in devices:
            errors.append(f"{path}: device {device!r} does not exist in current lab")
            return None
        return device

    def _validate_requiring_startup(
        self, value: Any, devices: set[str], lab_dir: Path, errors: list[str]
    ) -> None:
        if value is None:
            return
        items = _list(value, "$.test.requiring_startup", errors)
        if items is None:
            return
        seen: set[str] = set()
        for index, device in enumerate(items):
            path = f"$.test.requiring_startup[{index}]"
            valid_device = self._device(device, devices, path, errors)
            if valid_device is None:
                continue
            if valid_device in seen:
                errors.append(f"{path}: duplicate device {valid_device!r}")
            seen.add(valid_device)
            if not (lab_dir / f"{valid_device}.startup").is_file():
                errors.append(f"{path}: required {valid_device}.startup is missing")

    def _validate_ip_mapping(
        self,
        value: Any,
        topology: dict[str, dict[str, str]],
        lab_dir: Path,
        errors: list[str],
    ) -> dict[str, dict[str, ipaddress.IPv4Interface | ipaddress.IPv6Interface]]:
        parsed: dict[str, dict[str, ipaddress.IPv4Interface | ipaddress.IPv6Interface]] = {}
        if value is None:
            return parsed
        mapping = _mapping(value, "$.test.ip_mapping", errors)
        if mapping is None:
            return parsed
        devices = set(topology)
        globally_seen: dict[ipaddress.IPv4Address | ipaddress.IPv6Address, str] = {}
        for raw_device, raw_interfaces in mapping.items():
            device_path = f"$.test.ip_mapping[{raw_device!r}]"
            device = self._device(raw_device, devices, device_path, errors)
            interfaces = _mapping(raw_interfaces, device_path, errors)
            if device is None or interfaces is None:
                continue
            parsed[device] = {}
            startup = _startup_addresses(lab_dir, device)
            if interfaces and not startup:
                errors.append(
                    f"{device_path}: no supported IP assignment was found in {device}.startup"
                )
            for raw_interface, raw_ip in interfaces.items():
                path = f"{device_path}[{raw_interface!r}]"
                if not isinstance(raw_interface, str) or not _INTERFACE_RE.fullmatch(raw_interface):
                    errors.append(f"{path}: invalid interface key")
                    continue
                if not _is_canonical_interface_reference(raw_interface):
                    errors.append(
                        f"{path}: interface key must use canonical form without leading zeroes"
                    )
                interface = _normalise_interface(raw_interface)
                if interface not in topology[device]:
                    errors.append(f"{path}: interface does not belong to device {device!r}")
                ip_text = _string(raw_ip, path, errors)
                if ip_text is None:
                    continue
                try:
                    ip_value = ipaddress.ip_interface(ip_text)
                except ValueError as exc:
                    errors.append(f"{path}: invalid IP/prefix {ip_text!r}: {exc}")
                    continue
                parsed[device][interface] = ip_value
                previous = globally_seen.get(ip_value.ip)
                if previous is not None:
                    errors.append(f"{path}: duplicate IP address {ip_value.ip} (already used at {previous})")
                else:
                    globally_seen[ip_value.ip] = path
                if str(ip_value) not in startup.get(interface, set()):
                    errors.append(
                        f"{path}: {ip_value} is not configured on eth{interface} in {device}.startup"
                    )
        return parsed

    def _validate_daemons(self, value: Any, devices: set[str], errors: list[str]) -> None:
        if value is None:
            return
        mapping = _mapping(value, "$.test.daemons", errors)
        if mapping is None:
            return
        for raw_device, raw_daemons in mapping.items():
            path = f"$.test.daemons[{raw_device!r}]"
            self._device(raw_device, devices, path, errors)
            daemons = _list(raw_daemons, path, errors)
            if daemons is None:
                continue
            seen: set[str] = set()
            for index, daemon in enumerate(daemons):
                daemon_path = f"{path}[{index}]"
                if not isinstance(daemon, str) or not _DAEMON_RE.fullmatch(daemon):
                    errors.append(f"{daemon_path}: invalid daemon assertion")
                elif daemon in seen:
                    errors.append(f"{daemon_path}: duplicate daemon assertion {daemon!r}")
                else:
                    seen.add(daemon)

    def _validate_kernel_routes(
        self,
        value: Any,
        topology: dict[str, dict[str, str]],
        ip_mapping: dict[str, dict[str, ipaddress.IPv4Interface | ipaddress.IPv6Interface]],
        errors: list[str],
    ) -> None:
        if value is None:
            return
        mapping = _mapping(value, "$.test.kernel_routes", errors)
        if mapping is None:
            return
        devices = set(topology)
        for raw_device, raw_routes in mapping.items():
            path = f"$.test.kernel_routes[{raw_device!r}]"
            device = self._device(raw_device, devices, path, errors)
            routes = _list(raw_routes, path, errors)
            if device is None or routes is None:
                continue
            seen_routes: set[str] = set()
            connected = {interface.network for interface in ip_mapping.get(device, {}).values()}
            for index, route_entry in enumerate(routes):
                route_path = f"{path}[{index}]"
                destination: Any
                next_hops: list[Any] = []
                if isinstance(route_entry, str):
                    destination = route_entry
                elif isinstance(route_entry, list) and len(route_entry) == 2:
                    destination, raw_next_hops = route_entry
                    if isinstance(raw_next_hops, list):
                        next_hops = raw_next_hops
                    else:
                        errors.append(f"{route_path}[1]: expected a list of next-hop identifiers")
                else:
                    errors.append(f"{route_path}: expected prefix or [prefix, [next-hops...]]")
                    continue
                if not isinstance(destination, str):
                    errors.append(f"{route_path}: route prefix must be a string")
                    continue
                try:
                    network = ipaddress.ip_network(destination, strict=True)
                except ValueError as exc:
                    errors.append(f"{route_path}: invalid route prefix {destination!r}: {exc}")
                    continue
                if network.version != 4:
                    errors.append(
                        f"{route_path}: checker 0.1.14 kernel route checks support IPv4 only"
                    )
                    continue
                canonical = str(network)
                if canonical in seen_routes:
                    errors.append(f"{route_path}: duplicate route {canonical}")
                seen_routes.add(canonical)
                if network in connected:
                    errors.append(f"{route_path}: directly-connected route {canonical} must not be listed")
                if isinstance(route_entry, list) and not next_hops:
                    errors.append(f"{route_path}[1]: next-hop list must not be empty")
                    continue
                ip_hops = 0
                interface_hops = 0
                seen_hops: set[str] = set()
                for hop_index, hop in enumerate(next_hops):
                    hop_path = f"{route_path}[1][{hop_index}]"
                    if not isinstance(hop, str) or not hop:
                        errors.append(f"{hop_path}: next-hop identifier must be a non-empty string")
                        continue
                    if hop in seen_hops:
                        errors.append(f"{hop_path}: duplicate next-hop identifier {hop!r}")
                    seen_hops.add(hop)
                    try:
                        gateway = ipaddress.ip_address(hop)
                    except ValueError:
                        interface_hops += 1
                        if not re.fullmatch(r"eth[0-9]+", hop):
                            errors.append(
                                f"{hop_path}: checker route interfaces must use the ethN form"
                            )
                        elif not _is_canonical_interface_reference(hop):
                            errors.append(
                                f"{hop_path}: interface must use canonical ethN form without leading zeroes"
                            )
                        interface = _normalise_interface(hop)
                        if interface not in topology[device]:
                            errors.append(f"{hop_path}: interface {hop!r} does not belong to {device!r}")
                    else:
                        ip_hops += 1
                        if gateway.version != network.version:
                            errors.append(
                                f"{hop_path}: gateway IP family does not match route {canonical}"
                            )
                        device_interfaces = list(ip_mapping.get(device, {}).values())
                        if any(gateway == interface.ip for interface in device_interfaces):
                            errors.append(f"{hop_path}: gateway {gateway} is an address of {device!r}")
                        if device_interfaces and not any(
                            gateway.version == interface.version and gateway in interface.network
                            for interface in device_interfaces
                        ):
                            errors.append(f"{hop_path}: gateway {gateway} is not on a subnet of {device!r}")
                if ip_hops and interface_hops:
                    errors.append(
                        f"{route_path}[1]: checker 0.1.14 treats gateway and interface as separate "
                        "next hops; use only one identifier per single path"
                    )

    def _validate_reachability(
        self,
        value: Any,
        devices: set[str],
        ip_mapping: dict[str, dict[str, ipaddress.IPv4Interface | ipaddress.IPv6Interface]],
        errors: list[str],
    ) -> None:
        if value is None:
            return
        mapping = _mapping(value, "$.test.reachability", errors)
        if mapping is None:
            return
        known_ips = {interface.ip for interfaces in ip_mapping.values() for interface in interfaces.values()}
        for raw_device, raw_destinations in mapping.items():
            path = f"$.test.reachability[{raw_device!r}]"
            self._device(raw_device, devices, path, errors)
            destinations = _list(raw_destinations, path, errors)
            if destinations is None:
                continue
            seen: set[str] = set()
            for index, raw_destination in enumerate(destinations):
                destination_path = f"{path}[{index}]"
                destination = _string(raw_destination, destination_path, errors)
                if destination is None:
                    continue
                target = destination[1:] if destination.startswith("!") else destination
                if not target or not _SAFE_COMMAND_DESTINATION_RE.fullmatch(target):
                    errors.append(f"{destination_path}: unsafe ping destination")
                    continue
                if destination in seen:
                    errors.append(f"{destination_path}: duplicate destination {destination!r}")
                seen.add(destination)
                try:
                    address = ipaddress.ip_address(target)
                except ValueError:
                    if not _HOST_RE.fullmatch(target):
                        errors.append(f"{destination_path}: invalid IP address or DNS name {target!r}")
                else:
                    if address not in known_ips:
                        errors.append(f"{destination_path}: IP {address} is not present in current lab ip_mapping")

    def _validate_custom_commands(self, value: Any, devices: set[str], errors: list[str]) -> None:
        if value is None:
            return
        mapping = _mapping(value, "$.test.custom_commands", errors)
        if mapping is None:
            return
        for raw_device, raw_commands in mapping.items():
            path = f"$.test.custom_commands[{raw_device!r}]"
            self._device(raw_device, devices, path, errors)
            commands = _list(raw_commands, path, errors)
            if commands is None:
                continue
            for index, raw_command in enumerate(commands):
                command_path = f"{path}[{index}]"
                command = _mapping(raw_command, command_path, errors)
                if command is None:
                    continue
                self._validate_keys(command, self._custom_keys, command_path, errors)
                _string(command.get("command"), f"{command_path}.command", errors)
                assertions = self._custom_keys.intersection(command) - {"command"}
                if not assertions:
                    errors.append(
                        f"{command_path}: at least one of regex_match, output, or exit_code is required"
                    )
                if "regex_match" in command:
                    regex = _string(command["regex_match"], f"{command_path}.regex_match", errors, nonempty=False)
                    if regex is not None:
                        try:
                            re.compile(regex)
                        except re.error as exc:
                            errors.append(f"{command_path}.regex_match: invalid regex: {exc}")
                if "output" in command:
                    _string(command["output"], f"{command_path}.output", errors, nonempty=False)
                if "exit_code" in command and not _is_int(command["exit_code"]):
                    errors.append(f"{command_path}.exit_code: expected an integer")

    def _validate_protocols(
        self,
        value: Any,
        devices: set[str],
        topology: dict[str, dict[str, str]],
        errors: list[str],
    ) -> None:
        if value is None:
            return
        protocols = _mapping(value, "$.test.protocols", errors)
        if protocols is None:
            return
        for protocol, raw_config in protocols.items():
            protocol_path = f"$.test.protocols[{protocol!r}]"
            if not isinstance(protocol, str) or protocol not in self._protocols:
                if self._documented_keys:
                    errors.append(f"{protocol_path}: unsupported protocol")
                continue
            config = _mapping(raw_config, protocol_path, errors)
            if config is None:
                continue
            self._validate_keys(
                config,
                self._protocol_keys.get(protocol, set()),
                protocol_path,
                errors,
            )
            for generic in ("networks", "injections"):
                if generic in config:
                    self._validate_device_string_lists(
                        config[generic], devices, f"{protocol_path}.{generic}", errors,
                        networks=(generic == "networks"),
                    )
            if protocol == "bgpd":
                self._validate_bgp(config, devices, errors, protocol_path)
            elif protocol == "ospfd":
                self._validate_ospf(config, devices, topology, errors, protocol_path)

    def _validate_device_string_lists(
        self,
        value: Any,
        devices: set[str],
        path: str,
        errors: list[str],
        *,
        networks: bool,
    ) -> None:
        mapping = _mapping(value, path, errors)
        if mapping is None:
            return
        for raw_device, raw_items in mapping.items():
            device_path = f"{path}[{raw_device!r}]"
            self._device(raw_device, devices, device_path, errors)
            items = _list(raw_items, device_path, errors)
            if items is None:
                continue
            for index, raw_item in enumerate(items):
                item_path = f"{device_path}[{index}]"
                item = _string(raw_item, item_path, errors)
                if item is None:
                    continue
                if networks:
                    try:
                        ipaddress.ip_network(item, strict=True)
                    except ValueError as exc:
                        errors.append(f"{item_path}: invalid network prefix: {exc}")
                elif not _DAEMON_RE.fullmatch(item):
                    errors.append(f"{item_path}: invalid redistribution assertion")

    def _validate_bgp(
        self, config: dict[Any, Any], devices: set[str], errors: list[str], path: str
    ) -> None:
        if "neighbors" in config:
            mapping = _mapping(config["neighbors"], f"{path}.neighbors", errors)
            if mapping is not None:
                for raw_device, raw_neighbors in mapping.items():
                    device_path = f"{path}.neighbors[{raw_device!r}]"
                    self._device(raw_device, devices, device_path, errors)
                    neighbors = _list(raw_neighbors, device_path, errors)
                    if neighbors is None:
                        continue
                    for index, raw_neighbor in enumerate(neighbors):
                        neighbor_path = f"{device_path}[{index}]"
                        neighbor = _mapping(raw_neighbor, neighbor_path, errors)
                        if neighbor is None:
                            continue
                        self._validate_keys(
                            neighbor, self._bgp_neighbor_keys, neighbor_path, errors
                        )
                        if set(neighbor) != {"ip", "asn"}:
                            errors.append(f"{neighbor_path}: exactly ip and asn are required")
                        ip_text = _string(neighbor.get("ip"), f"{neighbor_path}.ip", errors)
                        if ip_text is not None:
                            try:
                                ipaddress.ip_address(ip_text)
                            except ValueError as exc:
                                errors.append(f"{neighbor_path}.ip: invalid BGP peer IP: {exc}")
                        asn = neighbor.get("asn")
                        if not _is_int(asn) or not 1 <= asn <= 4_294_967_295:
                            errors.append(f"{neighbor_path}.asn: expected ASN in range 1..4294967295")
        if "routes" in config:
            mapping = _mapping(config["routes"], f"{path}.routes", errors)
            if mapping is not None:
                for raw_device, raw_routes in mapping.items():
                    device_path = f"{path}.routes[{raw_device!r}]"
                    self._device(raw_device, devices, device_path, errors)
                    routes = _list(raw_routes, device_path, errors)
                    if routes is None:
                        continue
                    for index, raw_route in enumerate(routes):
                        route_path = f"{device_path}[{index}]"
                        route = _mapping(raw_route, route_path, errors)
                        if route is None:
                            continue
                        self._validate_keys(route, self._bgp_route_keys, route_path, errors)
                        prefix = _string(route.get("route"), f"{route_path}.route", errors)
                        if prefix is not None:
                            try:
                                network = ipaddress.ip_network(prefix, strict=True)
                            except ValueError as exc:
                                errors.append(f"{route_path}.route: invalid prefix: {exc}")
                            else:
                                if network.version != 4:
                                    errors.append(
                                        f"{route_path}.route: BGP route checks support IPv4 only in checker 0.1.14"
                                    )
                        alternatives = _list(route.get("aspath"), f"{route_path}.aspath", errors)
                        if alternatives is not None:
                            for alt_index, alternative in enumerate(alternatives):
                                alt_path = f"{route_path}.aspath[{alt_index}]"
                                asns = _list(alternative, alt_path, errors)
                                if asns is not None and any(not _is_int(asn) for asn in asns):
                                    errors.append(f"{alt_path}: AS path must contain integers")
        if "evpn_sessions" in config:
            self._validate_evpn_sessions(
                config["evpn_sessions"], devices, f"{path}.evpn_sessions", errors
            )
        if "vtep_devices" in config:
            mapping = _mapping(config["vtep_devices"], f"{path}.vtep_devices", errors)
            if mapping is not None:
                for raw_device, raw_info in mapping.items():
                    device_path = f"{path}.vtep_devices[{raw_device!r}]"
                    self._device(raw_device, devices, device_path, errors)
                    info = _mapping(raw_info, device_path, errors)
                    if info is None:
                        continue
                    self._validate_keys(info, self._vtep_device_keys, device_path, errors)
                    ip_text = _string(info.get("ip"), f"{device_path}.ip", errors)
                    if ip_text is not None:
                        try:
                            ipaddress.ip_address(ip_text)
                        except ValueError as exc:
                            errors.append(f"{device_path}.ip: invalid VTEP IP: {exc}")
                    vnis = _list(info.get("vnis"), f"{device_path}.vnis", errors)
                    if vnis is not None and any(
                        not _is_int(vni) or not 1 <= vni <= 16_777_215 for vni in vnis
                    ):
                        errors.append(f"{device_path}.vnis: VNIs must be integers 1..16777215")

    def _validate_ospf(
        self,
        config: dict[Any, Any],
        devices: set[str],
        topology: dict[str, dict[str, str]],
        errors: list[str],
        path: str,
    ) -> None:
        if "neighbors" in config:
            mapping = _mapping(config["neighbors"], f"{path}.neighbors", errors)
            if mapping is not None:
                for raw_device, raw_neighbors in mapping.items():
                    device_path = f"{path}.neighbors[{raw_device!r}]"
                    self._device(raw_device, devices, device_path, errors)
                    neighbors = _list(raw_neighbors, device_path, errors)
                    if neighbors is None:
                        continue
                    for index, raw_neighbor in enumerate(neighbors):
                        neighbor_path = f"{device_path}[{index}]"
                        neighbor = _mapping(raw_neighbor, neighbor_path, errors)
                        if neighbor is None:
                            continue
                        self._validate_keys(
                            neighbor, self._ospf_neighbor_keys, neighbor_path, errors
                        )
                        router_id = _string(neighbor.get("router_id"), f"{neighbor_path}.router_id", errors)
                        if router_id is not None:
                            try:
                                ipaddress.IPv4Address(router_id)
                            except ValueError as exc:
                                errors.append(f"{neighbor_path}.router_id: invalid IPv4 router ID: {exc}")
                        if "state" in neighbor:
                            _string(neighbor["state"], f"{neighbor_path}.state", errors)
        if "routes" in config:
            mapping = _mapping(config["routes"], f"{path}.routes", errors)
            if mapping is not None:
                for raw_device, raw_routes in mapping.items():
                    device_path = f"{path}.routes[{raw_device!r}]"
                    self._device(raw_device, devices, device_path, errors)
                    routes = _list(raw_routes, device_path, errors)
                    if routes is None:
                        continue
                    for index, raw_route in enumerate(routes):
                        route_path = f"{device_path}[{index}]"
                        route = _mapping(raw_route, route_path, errors)
                        if route is None:
                            continue
                        self._validate_keys(route, self._ospf_route_keys, route_path, errors)
                        prefix = _string(route.get("route"), f"{route_path}.route", errors)
                        if prefix is not None:
                            try:
                                network = ipaddress.ip_network(prefix, strict=True)
                            except ValueError as exc:
                                errors.append(f"{route_path}.route: invalid prefix: {exc}")
                            else:
                                if network.version != 4:
                                    errors.append(
                                        f"{route_path}.route: OSPF route checks support IPv4 only in checker 0.1.14"
                                    )
        if "interfaces" in config:
            mapping = _mapping(config["interfaces"], f"{path}.interfaces", errors)
            if mapping is not None:
                for raw_device, raw_interfaces in mapping.items():
                    device_path = f"{path}.interfaces[{raw_device!r}]"
                    device = self._device(raw_device, devices, device_path, errors)
                    interfaces = _mapping(raw_interfaces, device_path, errors)
                    if device is None or interfaces is None:
                        continue
                    for interface, expected in interfaces.items():
                        interface_path = f"{device_path}[{interface!r}]"
                        if not isinstance(interface, str) or not re.fullmatch(r"eth[0-9]+", interface):
                            errors.append(
                                f"{interface_path}: checker OSPF interfaces must use the ethN form"
                            )
                        elif not _is_canonical_interface_reference(interface):
                            errors.append(
                                f"{interface_path}: interface must use canonical ethN form without leading zeroes"
                            )
                        if not isinstance(interface, str) or _normalise_interface(interface) not in topology[device]:
                            errors.append(f"{interface_path}: interface does not belong to {device!r}")
                        if not isinstance(expected, dict) or not expected:
                            errors.append(f"{interface_path}: expected non-empty FRR field mapping")

    def _validate_evpn_sessions(
        self, value: Any, devices: set[str], path: str, errors: list[str]
    ) -> None:
        mapping = _mapping(value, path, errors)
        if mapping is None:
            return
        for raw_device, raw_neighbors in mapping.items():
            device_path = f"{path}[{raw_device!r}]"
            self._device(raw_device, devices, device_path, errors)
            neighbors = _list(raw_neighbors, device_path, errors)
            if neighbors is None:
                continue
            for index, raw_neighbor in enumerate(neighbors):
                neighbor_path = f"{device_path}[{index}]"
                neighbor = _string(raw_neighbor, neighbor_path, errors)
                if neighbor is None:
                    continue
                try:
                    ipaddress.ip_address(neighbor)
                except ValueError as exc:
                    errors.append(f"{neighbor_path}: invalid EVPN peer IP: {exc}")

    def _validate_applications(
        self,
        value: Any,
        devices: set[str],
        ip_mapping: dict[str, dict[str, ipaddress.IPv4Interface | ipaddress.IPv6Interface]],
        raw_ip_mapping: Any,
        errors: list[str],
    ) -> None:
        if value is None:
            return
        applications = _mapping(value, "$.test.applications", errors)
        if applications is None:
            return
        self._validate_keys(
            applications, self._application_keys, "$.test.applications", errors
        )
        known_ips = {
            str(interface.ip)
            for interfaces in ip_mapping.values()
            for interface in interfaces.values()
        }
        checker_dns_ip_literals = _raw_ip_literals(raw_ip_mapping)
        if "dns" in applications:
            dns = _mapping(applications["dns"], "$.test.applications.dns", errors)
            if dns is not None:
                self._validate_keys(
                    dns, self._dns_keys, "$.test.applications.dns", errors
                )
                if not dns:
                    errors.append("$.test.applications.dns: mapping must not be empty")
                if "authoritative" in dns:
                    if "local_ns" not in dns:
                        errors.append(
                            "$.test.applications.dns.authoritative: local_ns is required by checker 0.1.14"
                        )
                    if not checker_dns_ip_literals:
                        errors.append(
                            "$.test.applications.dns.authoritative: ip_mapping is required by checker 0.1.14"
                        )
                if "records" in dns and "local_ns" not in dns:
                    errors.append(
                        "$.test.applications.dns.records: local_ns is required by checker 0.1.14"
                    )
                self._validate_dns(dns, devices, checker_dns_ip_literals, errors)
        if "http" in applications:
            self._validate_http(applications["http"], devices, errors)

    def _validate_dns(
        self, dns: dict[Any, Any], devices: set[str], known_ips: set[str], errors: list[str]
    ) -> None:
        if "authoritative" in dns:
            authoritative = _mapping(dns["authoritative"], "$.test.applications.dns.authoritative", errors)
            if authoritative is not None:
                if not authoritative:
                    errors.append("$.test.applications.dns.authoritative: mapping must not be empty")
                for zone, raw_ips in authoritative.items():
                    zone_path = f"$.test.applications.dns.authoritative[{zone!r}]"
                    _string(zone, zone_path, errors)
                    ips = _list(raw_ips, zone_path, errors)
                    if ips is None:
                        continue
                    if not ips:
                        errors.append(f"{zone_path}: authority IP list must not be empty")
                    for index, raw_ip in enumerate(ips):
                        ip_path = f"{zone_path}[{index}]"
                        ip_text = _string(raw_ip, ip_path, errors)
                        if ip_text is None:
                            continue
                        try:
                            ipaddress.ip_address(ip_text)
                        except ValueError as exc:
                            errors.append(f"{ip_path}: invalid authority IP: {exc}")
                        if ip_text not in known_ips:
                            errors.append(f"{ip_path}: authority IP is absent from ip_mapping")
        if "local_ns" in dns:
            local_ns = _mapping(dns["local_ns"], "$.test.applications.dns.local_ns", errors)
            if local_ns is not None:
                if not local_ns:
                    errors.append("$.test.applications.dns.local_ns: mapping must not be empty")
                for raw_ip, raw_devices in local_ns.items():
                    ip_path = f"$.test.applications.dns.local_ns[{raw_ip!r}]"
                    if not isinstance(raw_ip, str):
                        errors.append(f"{ip_path}: resolver IP key must be a string")
                    else:
                        try:
                            ipaddress.ip_address(raw_ip)
                        except ValueError as exc:
                            errors.append(f"{ip_path}: invalid resolver IP: {exc}")
                        if raw_ip not in known_ips:
                            errors.append(f"{ip_path}: resolver IP is absent from ip_mapping")
                    managed = _list(raw_devices, ip_path, errors)
                    if managed is not None:
                        if not managed:
                            errors.append(f"{ip_path}: managed device list must not be empty")
                        for index, device in enumerate(managed):
                            self._device(device, devices, f"{ip_path}[{index}]", errors)
        if "records" in dns:
            records = _mapping(dns["records"], "$.test.applications.dns.records", errors)
            if records is not None:
                if not records:
                    errors.append("$.test.applications.dns.records: mapping must not be empty")
                for record_type, raw_names in records.items():
                    type_path = f"$.test.applications.dns.records[{record_type!r}]"
                    if not isinstance(record_type, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", record_type):
                        errors.append(f"{type_path}: invalid DNS record type")
                    names = _mapping(raw_names, type_path, errors)
                    if names is None:
                        continue
                    if not names:
                        errors.append(f"{type_path}: record-name mapping must not be empty")
                    for name, raw_values in names.items():
                        name_path = f"{type_path}[{name!r}]"
                        _string(name, name_path, errors)
                        values = _list(raw_values, name_path, errors)
                        if values is not None:
                            if not values:
                                errors.append(f"{name_path}: expected record values must not be empty")
                            for index, expected in enumerate(values):
                                value_path = f"{name_path}[{index}]"
                                expected_text = _string(expected, value_path, errors)
                                normalized_type = record_type.upper() if isinstance(record_type, str) else ""
                                if expected_text is None or normalized_type not in {"A", "AAAA"}:
                                    continue
                                try:
                                    address = ipaddress.ip_address(expected_text)
                                except ValueError as exc:
                                    errors.append(
                                        f"{value_path}: invalid {normalized_type} record address: {exc}"
                                    )
                                    continue
                                expected_version = 4 if normalized_type == "A" else 6
                                if address.version != expected_version:
                                    errors.append(
                                        f"{value_path}: {normalized_type} records require IPv{expected_version} addresses"
                                    )

    def _validate_http(self, value: Any, devices: set[str], errors: list[str]) -> None:
        mapping = _mapping(value, "$.test.applications.http", errors)
        if mapping is None:
            return
        if not mapping:
            errors.append("$.test.applications.http: mapping must not be empty")
        for raw_device, raw_checks in mapping.items():
            path = f"$.test.applications.http[{raw_device!r}]"
            self._device(raw_device, devices, path, errors)
            checks = _list(raw_checks, path, errors)
            if checks is None:
                continue
            if not checks:
                errors.append(f"{path}: HTTP check list must not be empty")
            for index, raw_check in enumerate(checks):
                check_path = f"{path}[{index}]"
                check = _mapping(raw_check, check_path, errors)
                if check is None:
                    continue
                self._validate_keys(check, self._http_keys, check_path, errors)
                url = _string(check.get("url"), f"{check_path}.url", errors)
                if url is not None:
                    try:
                        parsed = urlsplit(url)
                    except ValueError as exc:
                        errors.append(f"{check_path}.url: invalid URL: {exc}")
                    else:
                        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                            errors.append(f"{check_path}.url: expected an absolute HTTP(S) URL")
                    if any(character in url for character in ("'", '"', "`", "\n", "\r")):
                        errors.append(f"{check_path}.url: unsafe characters are not allowed")
                if "method" in check:
                    method = _string(check["method"], f"{check_path}.method", errors)
                    if method is not None and not _METHOD_RE.fullmatch(method.upper()):
                        errors.append(f"{check_path}.method: invalid HTTP method")
                if "status_code" in check:
                    status = check["status_code"]
                    if not _is_int(status) or not 100 <= status <= 599:
                        errors.append(f"{check_path}.status_code: expected integer 100..599")
                if "regex_body" in check:
                    regex = _string(check["regex_body"], f"{check_path}.regex_body", errors, nonempty=False)
                    if regex is not None:
                        try:
                            re.compile(regex)
                        except re.error as exc:
                            errors.append(f"{check_path}.regex_body: invalid regex: {exc}")
                if "body_contains" in check:
                    _string(check["body_contains"], f"{check_path}.body_contains", errors, nonempty=False)

__all__ = ["YamlValidator", "schema_support_errors"]
