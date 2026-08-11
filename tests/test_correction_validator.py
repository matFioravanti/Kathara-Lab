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


def test_unrecognized_sections_are_accepted(tmp_path: Path):
    """A correction with unrecognized sections is valid for the sanity check; the checker will decide."""
    yaml = (
        'lab_inline: "r1[0]=A"\n'
        'test:\n'
        '  requiring_startup: [r1]\n'
        '  some_unrecognized_test_type: true\n'
        'unknown_top_level_key: 123\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert result.valid, result.errors


def test_custom_command_missing_assertions_is_accepted(tmp_path: Path):
    """The validator no longer checks for assertions, leaving that to the checker."""
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  custom_commands:\n    r1:\n'
        '      - command: sysctl net.ipv4.ip_forward\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert result.valid, result.errors


def test_benign_redirection_is_accepted(tmp_path: Path):
    """The validator should allow benign shell redirections like > and 2>/dev/null."""
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  custom_commands:\n    r1:\n'
        '      - command: sysctl net.ipv4.ip_forward > /tmp/output\n'
        '      - command: ping -c 1 8.8.8.8 2>/dev/null\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert result.valid, result.errors


# ---------------------------------------------------------------------------
# Rejected cases
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


def test_correction_with_missing_test_is_rejected(tmp_path: Path):
    """A correction with lab_inline but no test block must be rejected."""
    yaml = 'lab_inline: |\n  r1[0]="A"\n'
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("test" in e for e in result.errors)


def test_destructive_custom_command_is_rejected(tmp_path: Path):
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  custom_commands:\n    r1:\n'
        '      - command: rm -rf /\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("destructive" in e for e in result.errors)


def test_other_destructive_custom_commands_are_rejected(tmp_path: Path):
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  custom_commands:\n    r1:\n'
        '      - command: reboot\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("destructive" in e for e in result.errors)


def test_ambiguous_kernel_routes_are_rejected(tmp_path: Path):
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  kernel_routes:\n    r1:\n'
        '      - ["192.168.1.0/24", ["10.0.0.1", "eth0"]]\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert not result.valid
    assert any("ambiguous next-hop list" in e for e in result.errors)


def test_valid_kernel_routes_are_accepted(tmp_path: Path):
    yaml = (
        'lab_inline: |\n  r1[0]="A"\n'
        'test:\n  kernel_routes:\n    r1:\n'
        '      - ["192.168.1.0/24", ["10.0.0.1"]]\n'
        '      - ["192.168.2.0/24", ["eth0"]]\n'
        '      - ["192.168.3.0/24", ["10.0.0.1", "10.0.0.2"]]\n'
    )
    result = CorrectionValidator().validate(_write(tmp_path, yaml))
    assert result.valid
