from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from kathara_pipeline.yaml_validator import YamlValidator


def _write_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    lab = tmp_path / "source"
    lab.mkdir()
    (lab / "lab.conf").write_text(
        'r1[0]="lan"\n'
        'r1[image]="kathara/core:latest"\n'
        'pc1[0]="lan"\n'
        'pc1[image]="kathara/core:latest"\n'
        'monitor[bridged]="true"\n'
        'monitor[image]="kathara/core:latest"\n',
        encoding="utf-8",
    )
    (lab / "r1.startup").write_text(
        "ip address replace 10.0.0.1/24 dev eth0\n", encoding="utf-8"
    )
    (lab / "pc1.startup").write_text(
        "ip -4 address replace 10.0.0.2/24 dev eth0\n"
        "ip route replace default via 10.0.0.1 dev eth0\n",
        encoding="utf-8",
    )
    schema = tmp_path / "config-schema.md"
    fixture_schema = Path(__file__).resolve().parent / "fixtures" / "config-schema.md"
    if not fixture_schema.is_file():
        raise FileNotFoundError(
            f"Fixture dello schema non trovata: {fixture_schema}"
        )
    schema.write_text(fixture_schema.read_text(encoding="utf-8"), encoding="utf-8")
    correction = tmp_path / "correction.yaml"
    return lab, schema, correction


def _valid_document() -> dict:
    return {
        "lab_inline": 'r1[0]="lan"\npc1[0]="lan"\n',
        "convergence_time": 10,
        "default_image": "kathara/core:latest",
        "test": {
            "requiring_startup": ["r1", "pc1"],
            "ip_mapping": {
                "r1": {"0": "10.0.0.1/24"},
                "pc1": {"0": "10.0.0.2/24"},
            },
            "kernel_routes": {"pc1": [["0.0.0.0/0", ["10.0.0.1"]]]},
            "reachability": {"pc1": ["10.0.0.1"]},
            "custom_commands": {
                "r1": [{"command": "sysctl net.ipv4.ip_forward", "exit_code": 0}]
            },
        },
    }


def _write_yaml(path: Path, document: dict) -> None:
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def test_valid_document_uses_documented_structural_mode(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert result.valid, result.errors
    assert result.mode == "documented-structural"
    assert result.data == document


def test_safe_load_rejects_python_object_tags(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    correction.write_text("!!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8")

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("Invalid YAML syntax" in error for error in result.errors)


def test_top_level_must_be_mapping_and_duplicate_keys_are_rejected(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    correction.write_text("lab_inline: x\nlab_inline: y\n", encoding="utf-8")

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("duplicate YAML key" in error for error in result.errors)

    correction.write_text("- not\n- a mapping\n", encoding="utf-8")
    result = YamlValidator(schema).validate(correction, lab, tmp_path)
    assert not result.valid
    assert any("top-level mapping" in error for error in result.errors)


def test_comments_are_rejected_but_hashes_inside_lab_inline_are_data(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    _write_yaml(correction, document)
    with correction.open("a", encoding="utf-8") as stream:
        stream.write("# generated explanation\n")

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("must not contain comments" in error for error in result.errors)


def test_unknown_keys_placeholder_and_missing_custom_assertion_are_rejected(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["mystery"] = True
    document["test"]["custom_commands"]["r1"] = [{"command": "TODO inspect"}]
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("unknown key 'mystery'" in error for error in result.errors)
    assert any("placeholder token" in error for error in result.errors)
    assert any("at least one of" in error for error in result.errors)


def test_device_interface_and_startup_ip_must_match_lab(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["ip_mapping"] = {
        "ghost": {"0": "10.0.0.3/24"},
        "r1": {"2": "10.0.0.9/24", "0": "10.0.0.99/24"},
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("ghost" in error and "does not exist" in error for error in result.errors)
    assert any("interface does not belong" in error for error in result.errors)
    assert any("not configured" in error for error in result.errors)


def test_ip_mapping_fails_when_startup_address_cannot_be_verified(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    (lab / "r1.startup").write_text("echo no-address-command\n", encoding="utf-8")
    document = _valid_document()
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("no supported IP assignment" in error for error in result.errors)


def test_ifconfig_style_startup_address_is_recognised(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    (lab / "r1.startup").write_text(
        "ifconfig eth0 10.0.0.1 netmask 255.255.255.0\n", encoding="utf-8"
    )
    document = _valid_document()
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert result.valid, result.errors


def test_markdown_schema_content_actually_governs_allowed_test_keys(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    schema.write_text(
        "# Minimal schema\n"
        "```yaml\n"
        "lab_inline: |\n  r1[0]=\"lan\"\n"
        "convergence_time: 10\n"
        "default_image: kathara/core\n"
        "test:\n"
        "  requiring_startup: []\n"
        "  ip_mapping: {}\n"
        "  kernel_routes: {}\n"
        "  reachability: {}\n"
        "  custom_commands:\n"
        "    r1:\n"
        "      - command: 'true'\n"
        "        exit_code: 0\n"
        "```\n",
        encoding="utf-8",
    )
    document = _valid_document()
    document["test"]["daemons"] = {"r1": ["zebra"]}
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("daemons" in error and "unknown key" in error for error in result.errors)


def test_new_markdown_field_is_detected_as_unsupported_not_silently_discarded(
    tmp_path: Path,
) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    schema.write_text(
        "# Future schema\n"
        "```yaml\n"
        "lab_inline: |\n  r1[0]=\"lan\"\n"
        "test:\n"
        "  future_check: {}\n"
        "```\n",
        encoding="utf-8",
    )
    correction.write_text(
        "lab_inline: |\n  r1[0]=\"lan\"\n  pc1[0]=\"lan\"\n"
        "test:\n  future_check: {}\n",
        encoding="utf-8",
    )

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("$.test.future_check" in error and "not supported" in error for error in result.errors)
    assert not any("unknown key 'future_check'" in error for error in result.errors)


def test_noncanonical_ipv6_ip_mapping_is_rejected_for_dns_runtime_compatibility(
    tmp_path: Path,
) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    (lab / "r1.startup").write_text(
        "ip -6 address replace 2001:db8::1/64 dev eth0\n", encoding="utf-8"
    )
    document = _valid_document()
    document["test"]["ip_mapping"]["r1"]["0"] = "2001:0db8:0:0:0:0:0:1/64"
    document["test"].pop("kernel_routes")
    document["test"]["reachability"] = {"pc1": ["10.0.0.2"]}
    document["test"]["applications"] = {
        "dns": {
            "authoritative": {"example.test": ["2001:db8::1"]},
            "local_ns": {"2001:db8::1": ["pc1"]},
        }
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("authority IP is absent from ip_mapping" in error for error in result.errors)


def test_noncanonical_ipv6_ip_mapping_is_valid_without_dns_lookup(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    (lab / "r1.startup").write_text(
        "ip -6 address replace 2001:db8::1/64 dev eth0\n", encoding="utf-8"
    )
    document = _valid_document()
    document["test"]["ip_mapping"]["r1"]["0"] = "2001:0db8:0:0:0:0:0:1/64"
    document["test"].pop("kernel_routes")
    document["test"]["reachability"] = {"pc1": ["10.0.0.2"]}
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert result.valid, result.errors


def test_interface_keys_with_leading_zeroes_are_rejected(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["ip_mapping"]["r1"] = {"00": "10.0.0.1/24"}
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("leading zeroes" in error for error in result.errors)


def test_bgp_and_ospf_route_checks_reject_ipv6_prefixes(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["protocols"] = {
        "bgpd": {"routes": {"r1": [{"route": "2001:db8::/64", "aspath": [[65000]]}]}},
        "ospfd": {"routes": {"r1": [{"route": "2001:db8::/64"}]}},
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("BGP route checks support IPv4 only" in error for error in result.errors)
    assert any("OSPF route checks support IPv4 only" in error for error in result.errors)


def test_skill_documented_ospf_injections_are_accepted(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "Supported: `protocols.<ripd|ospfd>.injections` redistribution checks.\n",
        encoding="utf-8",
    )
    document = _valid_document()
    document["test"]["protocols"] = {
        "ospfd": {"injections": {"r1": ["connected", "!bgp"]}}
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema, skill).validate(correction, lab, tmp_path)

    assert result.valid, result.errors


def test_kernel_route_checks_reject_ipv6_prefixes_unsupported_by_runtime(
    tmp_path: Path,
) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["kernel_routes"]["pc1"] = ["2001:db8::/64"]
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("kernel route checks support IPv4 only" in error for error in result.errors)


def test_kernel_route_gateway_must_match_destination_ip_family(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    with (lab / "lab.conf").open("a", encoding="utf-8") as stream:
        stream.write('r1[1]="v6"\npc1[1]="v6"\n')
    with (lab / "r1.startup").open("a", encoding="utf-8") as stream:
        stream.write("ip -6 address replace 2001:db8::1/64 dev eth1\n")
    with (lab / "pc1.startup").open("a", encoding="utf-8") as stream:
        stream.write("ip -6 address replace 2001:db8::2/64 dev eth1\n")
    document = _valid_document()
    document["lab_inline"] += 'r1[1]="v6"\npc1[1]="v6"\n'
    document["test"]["ip_mapping"]["r1"]["1"] = "2001:db8::1/64"
    document["test"]["ip_mapping"]["pc1"]["1"] = "2001:db8::2/64"
    document["test"]["kernel_routes"]["pc1"] = [
        ["0.0.0.0/0", ["2001:db8::1"]]
    ]
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("gateway IP family does not match route" in error for error in result.errors)


def test_inline_topology_must_match_and_cannot_contain_image_declarations(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["lab_inline"] = 'r1[0]="wrong"\nr1[image]="image"\n'
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("only numeric interface mappings" in error for error in result.errors)
    assert any("pc1" in error and "missing" in error for error in result.errors)
    assert any("collision domain" in error for error in result.errors)


def test_structure_and_labs_paths_cannot_escape_job(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document.pop("lab_inline")
    document["structure"] = "../outside.conf"
    document["labs_path"] = "/absolute/labs"
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("structure" in error and "escapes" in error for error in result.errors)
    assert any("labs_path" in error and "absolute" in error for error in result.errors)


def test_checker_014_compatibility_errors_are_caught(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["kernel_routes"]["pc1"] = [
        ["0.0.0.0/0", ["10.0.0.1", "eth0"]]
    ]
    document["test"]["applications"] = {
        "http": {"pc1": [{"url": "http://10.0.0.1/", "expected_status": 200}]}
    }
    document["test"]["protocols"] = {
        "ospfd": {"neighbors": {"r1": [{"ip": "10.0.0.2"}]}}
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("separate next hops" in error for error in result.errors)
    assert any("expected_status" in error and "unknown key" in error for error in result.errors)
    assert any("router_id" in error for error in result.errors)


def test_dns_checks_require_runtime_dependencies_and_nonempty_values(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["applications"] = {
        "dns": {"authoritative": {"example.test": []}, "records": {}}
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("local_ns is required" in error for error in result.errors)
    assert any("must not be empty" in error for error in result.errors)


def test_dns_a_and_aaaa_record_values_are_validated_by_ip_family(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["applications"] = {
        "dns": {
            "local_ns": {"10.0.0.1": ["pc1"]},
            "records": {
                "A": {"broken.example": ["999.0.0.1"]},
                "AAAA": {"wrong-family.example": ["10.0.0.1"]},
            },
        }
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("invalid A record address" in error for error in result.errors)
    assert any("AAAA records require IPv6" in error for error in result.errors)


def test_undocumented_runtime_only_checks_are_rejected(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["ipv6_enabled"] = ["r1"]
    document["test"]["bridges"] = {}
    document["test"]["protocols"] = {"sciond": {"address": {"r1": "1-ff00:0:1,127.0.0.1"}}}
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("ipv6_enabled" in error and "unknown key" in error for error in result.errors)
    assert any("bridges" in error and "unknown key" in error for error in result.errors)
    assert any("sciond" in error and "unsupported protocol" in error for error in result.errors)


def test_evpn_session_accepts_ipv4_and_ipv6_peer_strings(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["protocols"] = {
        "bgpd": {"evpn_sessions": {"r1": ["10.0.0.2", "2001:db8::2"]}}
    }
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert result.valid, result.errors


def test_reachability_rejects_shell_syntax_and_foreign_ip(tmp_path: Path) -> None:
    lab, schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["test"]["reachability"] = {"pc1": ["8.8.8.8", "10.0.0.1;reboot"]}
    _write_yaml(correction, document)

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert any("not present in current lab" in error for error in result.errors)
    assert any("unsafe ping destination" in error for error in result.errors)


def test_genuine_json_schema_is_applied(tmp_path: Path) -> None:
    pytest.importorskip("jsonschema")
    lab, _markdown_schema, correction = _write_fixture(tmp_path)
    document = _valid_document()
    document["convergence_time"] = 10
    _write_yaml(correction, document)
    schema = tmp_path / "config-schema.json"
    schema.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {"convergence_time": {"const": 99}},
            }
        ),
        encoding="utf-8",
    )

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert not result.valid
    assert result.mode == "json-schema"
    assert any("violates 'const'" in error for error in result.errors)


def test_genuine_json_schema_governs_future_shape_without_hardcoded_key_rejection(
    tmp_path: Path,
) -> None:
    pytest.importorskip("jsonschema")
    lab, _markdown_schema, correction = _write_fixture(tmp_path)
    correction.write_text("future_checker_field: enabled\n", encoding="utf-8")
    schema = tmp_path / "config-schema.json"
    schema.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["future_checker_field"],
                "additionalProperties": False,
                "properties": {"future_checker_field": {"const": "enabled"}},
            }
        ),
        encoding="utf-8",
    )

    result = YamlValidator(schema).validate(correction, lab, tmp_path)

    assert result.valid, result.errors
    assert result.mode == "json-schema"
