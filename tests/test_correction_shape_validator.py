import yaml
from pathlib import Path
from kathara_pipeline.correction_shape_validator import CorrectionShapeValidator

def test_shape_validator_identical(tmp_path: Path):
    ref_yaml = tmp_path / "ref.yaml"
    ref_yaml.write_text("""
test:
  reachability:
    pc1:
      - 10.0.0.1
    pc2:
      - 20.0.0.1
  ping:
    - 8.8.8.8
""")
    adapt_yaml = tmp_path / "adapt.yaml"
    adapt_yaml.write_text("""
test:
  reachability:
    hostA:
      - 192.168.1.1
    hostB:
      - 192.168.2.1
  ping:
    - 9.9.9.9
""")
    result = CorrectionShapeValidator.validate(ref_yaml, adapt_yaml)
    assert result.valid

def test_shape_validator_different_entries(tmp_path: Path):
    ref_yaml = tmp_path / "ref.yaml"
    ref_yaml.write_text("""
test:
  reachability:
    pc1:
      - 10.0.0.1
""")
    adapt_yaml = tmp_path / "adapt.yaml"
    adapt_yaml.write_text("""
test:
  reachability:
    pc1:
      - 10.0.0.1
    pc2:
      - 20.0.0.1
""")
    result = CorrectionShapeValidator.validate(ref_yaml, adapt_yaml)
    assert not result.valid
    assert "The adapted correction changed the structure of the reference correction." in result.errors[0]

def test_shape_validator_different_categories(tmp_path: Path):
    ref_yaml = tmp_path / "ref.yaml"
    ref_yaml.write_text("""
test:
  reachability:
    pc1:
      - 10.0.0.1
""")
    adapt_yaml = tmp_path / "adapt.yaml"
    adapt_yaml.write_text("""
test:
  ping:
    - 8.8.8.8
""")
    result = CorrectionShapeValidator.validate(ref_yaml, adapt_yaml)
    assert not result.valid

def test_shape_validator_complex_custom_commands(tmp_path: Path):
    ref_yaml = tmp_path / "ref.yaml"
    ref_yaml.write_text("""
test:
  custom_commands:
    - command: ip route
      expected: 10.0.0.0/24
""")
    adapt_yaml = tmp_path / "adapt.yaml"
    adapt_yaml.write_text("""
test:
  custom_commands:
    - command: ip a
      expected: 192.168.1.0/24
""")
    result = CorrectionShapeValidator.validate(ref_yaml, adapt_yaml)
    assert result.valid

def test_shape_validator_missing_custom_command_key(tmp_path: Path):
    ref_yaml = tmp_path / "ref.yaml"
    ref_yaml.write_text("""
test:
  custom_commands:
    - command: ip route
      expected: 10.0.0.0/24
""")
    adapt_yaml = tmp_path / "adapt.yaml"
    adapt_yaml.write_text("""
test:
  custom_commands:
    - command: ip a
""")
    result = CorrectionShapeValidator.validate(ref_yaml, adapt_yaml)
    assert not result.valid
