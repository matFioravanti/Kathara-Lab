from pathlib import Path

import pytest

from kathara_pipeline.lab_validator import LabValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_lab(root: Path, lab_conf_content: str = 'r1[0]="A"\nr2[0]="A"\n') -> Path:
    """Create a minimal valid lab directory."""
    lab = root / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text(lab_conf_content, encoding="utf-8")
    return lab


# ---------------------------------------------------------------------------
# Basic passing cases
# ---------------------------------------------------------------------------

def test_minimal_valid_lab_passes(tmp_path: Path):
    """A directory with a non-empty lab.conf is valid."""
    lab = _make_lab(tmp_path)
    result = LabValidator().validate(lab)
    assert result.valid, result.errors


def test_unquoted_collision_domain_passes(tmp_path: Path):
    """R1[0]=lan1 must pass — no Kathara syntax parsing."""
    lab = _make_lab(tmp_path, "R1[0]=lan1\nR2[0]=lan1\n")
    result = LabValidator().validate(lab)
    assert result.valid, result.errors


def test_hyphenated_domain_passes(tmp_path: Path):
    """r1-r2 domain names are now accepted — no Kathara-specific rejection."""
    lab = _make_lab(tmp_path, 'r1[0]="r1-r2"\nr2[0]="r1-r2"\n')
    result = LabValidator().validate(lab)
    assert result.valid, result.errors


def test_hyphenated_device_name_passes(tmp_path: Path):
    """Device identifiers with hyphens are accepted — no Kathara-specific rejection."""
    lab = _make_lab(tmp_path, 'r1-x[0]="A"\n')
    result = LabValidator().validate(lab)
    assert result.valid, result.errors


def test_startup_files_not_required(tmp_path: Path):
    """Startup files are optional — validator does not enforce machine/startup correspondence."""
    lab = _make_lab(tmp_path, 'r1[0]="A"\nr2[0]="A"\n')
    # No .startup files present — should still be valid
    result = LabValidator().validate(lab)
    assert result.valid, result.errors


def test_extra_startup_file_is_fine(tmp_path: Path):
    """A .startup file for a device not mentioned in lab.conf is now allowed."""
    lab = _make_lab(tmp_path)
    (lab / "ghost.startup").write_text("echo x\n", encoding="utf-8")
    result = LabValidator().validate(lab)
    assert result.valid, result.errors


def test_prompt_text_arg_is_ignored(tmp_path: Path):
    """prompt_text parameter exists for API compatibility but is not used for validation."""
    lab = _make_lab(tmp_path)
    result = LabValidator().validate(lab, "Create /etc/frr/frr.conf for r1 with 10.0.0.1/24")
    assert result.valid, result.errors


# ---------------------------------------------------------------------------
# Failing cases — objective filesystem checks
# ---------------------------------------------------------------------------

def test_missing_directory_fails(tmp_path: Path):
    result = LabValidator().validate(tmp_path / "nonexistent")
    assert not result.valid
    assert any("does not exist" in e for e in result.errors)


def test_missing_lab_conf_fails(tmp_path: Path):
    lab = tmp_path / "lab"
    lab.mkdir()
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("lab.conf" in e for e in result.errors)


def test_empty_lab_conf_fails(tmp_path: Path):
    lab = tmp_path / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text("   \n\t\n", encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("empty" in e for e in result.errors)


def test_placeholder_todo_fails(tmp_path: Path):
    lab = _make_lab(tmp_path, "r1[0]=A\nTODO fix routing\n")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("Placeholder" in e for e in result.errors)


def test_placeholder_change_me_fails(tmp_path: Path):
    lab = _make_lab(tmp_path, "r1[0]=A\n")
    (lab / "r1.startup").write_text("ip addr add CHANGE_ME dev eth0\n", encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("Placeholder" in e for e in result.errors)


def test_placeholder_angle_bracket_fails(tmp_path: Path):
    lab = _make_lab(tmp_path, "r1[0]=A\n")
    (lab / "r1.startup").write_text("ip addr add <ip_address>/24 dev eth0\n", encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("Placeholder" in e for e in result.errors)


def test_escaped_symlink_fails(tmp_path: Path):
    lab = _make_lab(tmp_path)
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    link = lab / "escape.conf"
    link.symlink_to(outside)
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("escapes" in e for e in result.errors)


def test_broken_symlink_fails(tmp_path: Path):
    lab = _make_lab(tmp_path)
    (lab / "broken.link").symlink_to(lab / "nonexistent_target")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("Broken" in e or "cyclic" in e for e in result.errors)


def test_nested_lab_conf_fails(tmp_path: Path):
    lab = _make_lab(tmp_path)
    subdir = lab / "r1"
    subdir.mkdir()
    (subdir / "lab.conf").write_text("nested\n", encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("Nested lab.conf" in e for e in result.errors)
