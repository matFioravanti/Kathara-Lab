from pathlib import Path

from kathara_pipeline.correction_validator import CorrectionValidator

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_YAML = '''\
lab_inline: |
  r1[0]="A"
  r2[0]="A"
convergence_time: 10
default_image: kathara/core
test:
  requiring_startup: [r1, r2]
  ip_mapping:
    r1: {eth0: 10.0.0.1/24}
    r2: {eth0: 10.0.0.2/24}
  reachability:
    r1: [10.0.0.2]
    r2: [10.0.0.1]
'''


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "correction.yaml"
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Accepted cases
# ---------------------------------------------------------------------------

def test_canonical_correction_is_candidate_independent_shape(tmp_path: Path):
    result = CorrectionValidator().validate(_write(tmp_path, _VALID_YAML))
    assert result.valid, result.errors


def test_valid_correction_with_lab_inline_is_accepted(tmp_path: Path):
    """Correction with non-empty lab_inline string must be accepted."""
    result = CorrectionValidator().validate(_write(tmp_path, _VALID_YAML))
    assert result.valid, result.errors


# ---------------------------------------------------------------------------
# Rejected cases – lab_inline
# ---------------------------------------------------------------------------

def test_correction_without_lab_inline_is_rejected(tmp_path: Path):
    """A correction that omits lab_inline entirely must be rejected."""
    yaml = 'convergence_time: 5\ntest:\n  requiring_startup: [r1]\n'
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("lab_inline" in e for e in result.errors)


def test_correction_with_empty_lab_inline_is_rejected(tmp_path: Path):
    """lab_inline present but empty string must be rejected."""
    yaml = 'lab_inline: ""\ntest:\n  requiring_startup: [r1]\n'
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("lab_inline" in e for e in result.errors)


def test_correction_with_whitespace_only_lab_inline_is_rejected(tmp_path: Path):
    """lab_inline with only whitespace must be rejected."""
    yaml = 'lab_inline: "   "\ntest:\n  requiring_startup: [r1]\n'
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("lab_inline" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Rejected cases – missing test
# ---------------------------------------------------------------------------

def test_correction_with_missing_test_is_rejected(tmp_path: Path):
    """A correction with lab_inline but no test block must be rejected."""
    yaml = 'lab_inline: |\n  r1[0]="A"\n'
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("test" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Rejected cases – structure key
# ---------------------------------------------------------------------------

def test_correction_using_structure_instead_of_lab_inline_is_rejected(tmp_path: Path):
    """Using structure instead of lab_inline must be rejected."""
    yaml = 'structure: /some/path\ntest:\n  requiring_startup: [r1]\n'
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("lab_inline" in e for e in result.errors)
    assert any("structure" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Pre-existing tests
# ---------------------------------------------------------------------------

def test_http_old_field_is_rejected(tmp_path: Path):
    yaml = (
        'lab_inline: |\n  s[0]="A"\n'
        'test:\n  applications:\n    http:\n      s:\n'
        '        - url: http://10.0.0.1/\n          expected_status: 200\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("status_code" in e for e in result.errors)


def test_custom_command_requires_assertion(tmp_path: Path):
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  custom_commands:\n    r1:\n'
        '      - command: sysctl net.ipv4.ip_forward\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("at least one" in e for e in result.errors)
