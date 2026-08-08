from __future__ import annotations

from pathlib import Path

import pytest

from kathara_pipeline.lab_validator import LabValidator, parse_lab_topology


LAB_CONF = """\
LAB_DESCRIPTION="test"
r1[0]="lan/00:00:00:00:00:01"
r1[image]="kathara/core:latest"
pc1[0]="lan"
pc1[image]="kathara/core:latest"
monitor[image]="kathara/core:latest"
"""


def _write_lab(root: Path) -> Path:
    lab = root / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text(LAB_CONF, encoding="utf-8")
    (lab / "r1.startup").write_text("ip address add 10.0.0.1/24 dev eth0\n", encoding="utf-8")
    (lab / "pc1.startup").write_text("ip address add 10.0.0.2/24 dev eth0\n", encoding="utf-8")
    return lab


def test_parse_lab_topology_normalises_domains_and_keeps_metadata_only_device(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)

    assert parse_lab_topology(lab) == {
        "r1": {"0": "lan"},
        "pc1": {"0": "lan"},
        "monitor": {},
    }


def test_valid_lab_returns_topology_data(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)

    result = LabValidator().validate(lab)

    assert result.valid
    assert result.errors == ()
    assert result.mode == "static"
    assert result.data == {"topology": parse_lab_topology(lab)}


def test_missing_lab_conf_is_reported(tmp_path: Path) -> None:
    lab = tmp_path / "lab"
    lab.mkdir()

    result = LabValidator().validate(lab)

    assert not result.valid
    assert any("Missing required lab.conf" in error for error in result.errors)


def test_malformed_duplicate_assignment_and_orphan_startup_are_reported(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)
    (lab / "lab.conf").write_text(
        'r1[0]="lan"\nr1[0]="other"\npc1[0]=\n', encoding="utf-8"
    )
    (lab / "ghost.startup").write_text("true\n", encoding="utf-8")

    result = LabValidator().validate(lab)

    assert not result.valid
    assert any("duplicate declaration" in error for error in result.errors)
    assert any("malformed device assignment" in error for error in result.errors)
    assert any("undeclared device" in error for error in result.errors)


def test_unrecognised_lab_conf_syntax_is_reported(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)
    with (lab / "lab.conf").open("a", encoding="utf-8") as stream:
        stream.write("this is not a Kathara assignment\n")

    result = LabValidator().validate(lab)

    assert not result.valid
    assert any("unrecognised syntax" in error for error in result.errors)


def test_placeholder_and_nested_lab_are_reported(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)
    (lab / "r1.startup").write_text("# TODO configure me\n", encoding="utf-8")
    nested = lab / "nested"
    nested.mkdir()
    (nested / "lab.conf").write_text('x[0]="x"\n', encoding="utf-8")
    (lab / "empty").mkdir()

    result = LabValidator().validate(lab)

    assert not result.valid
    assert any("Placeholder token" in error for error in result.errors)
    assert any("Nested lab.conf" in error for error in result.errors)


def test_prompt_required_file_and_all_startups_are_checked(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)

    result = LabValidator().validate(
        lab,
        "Ogni dispositivo deve avere un file .startup e il servizio usa `named.conf`.",
    )

    assert not result.valid
    assert any("monitor.startup" in error for error in result.errors)
    assert any("named.conf" in error for error in result.errors)


def test_prompt_required_zone_dockerfile_and_named_extensionless_file_are_detected(
    tmp_path: Path,
) -> None:
    lab = _write_lab(tmp_path)

    result = LabValidator().validate(
        lab,
        "Create db.root and Dockerfile; create the file named root-hints.",
    )

    assert not result.valid
    assert any("db.root" in error for error in result.errors)
    assert any("Dockerfile" in error for error in result.errors)
    assert any("root-hints" in error for error in result.errors)


def test_http_url_in_prompt_is_not_mistaken_for_a_required_lab_file(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)

    result = LabValidator().validate(
        lab,
        "pc1 must reach http://10.0.0.1/index.html after startup.",
    )

    assert result.valid, result.errors


def test_quoted_network_values_and_image_names_are_not_required_files(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)

    result = LabValidator().validate(
        lab,
        "Use IP `10.0.0.1`, subnet `10.0.0.0/24`, host `www.example.com`, "
        "and image `kathara/core`; run the commands/tests phase.",
    )

    assert result.valid, result.errors


def test_explicit_paths_and_unlisted_file_extensions_are_required(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)

    result = LabValidator().validate(
        lab,
        "The lab must include `r1/etc/systemd/system/frr.service`, `server.pem`, "
        "`script.py`, `.htaccess`, and r1/etc/hosts.",
    )

    assert not result.valid
    for expected in (
        "r1/etc/systemd/system/frr.service",
        "server.pem",
        "script.py",
        ".htaccess",
        "r1/etc/hosts",
    ):
        assert any(expected in error for error in result.errors)


def test_external_symlink_is_rejected(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)
    outside = tmp_path / "outside.conf"
    outside.write_text("secret\n", encoding="utf-8")
    link = lab / "r1" / "etc" / "outside.conf"
    link.parent.mkdir(parents=True)
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")

    result = LabValidator().validate(lab)

    assert not result.valid
    assert any("Symlink escapes" in error for error in result.errors)

def test_ipv4_fragments_and_versions_are_not_mistaken_for_files(tmp_path: Path) -> None:
    lab = _write_lab(tmp_path)
    
    # Prompt containing IPv4, CIDR, versions, decimals, and IPv6 in contexts that previously extracted fragments
    prompt = """
    Crea il file `lab.conf` e il file `r1.startup`.
    Use IP `192.168.1.1` and `192.168.1.10`.
    Configure `10.0.0.1/24` and `172.16.10.254`.
    Support IPv6 `2001:db8::1`.
    Subnet `10.0.0.0/24`.
    Use `version 1.10`.
    Also check `.1` and `.10` and `1.5`.
    Ensure the path `/etc/frr/frr.conf` is created.
    """
    
    result = LabValidator().validate(lab, prompt)
    
    # The lab lacks /etc/frr/frr.conf, so it SHOULD complain about that.
    # It should NOT complain about .1, .10, .24, .254, 1.10, 1.5, etc.
    assert not result.valid
    
    errors_str = " ".join(result.errors)
    
    # Verify true positive
    assert "etc/frr/frr.conf" in errors_str
    
    # Verify false positives are eliminated
    assert ".1" not in errors_str
    assert ".10" not in errors_str
    assert ".24" not in errors_str
    assert ".254" not in errors_str
    assert "1.10" not in errors_str
    assert "1.5" not in errors_str

