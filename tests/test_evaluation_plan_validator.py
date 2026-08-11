import pytest
from pathlib import Path

from kathara_pipeline.evaluation_plan_validator import EvaluationPlanValidator


def test_validator_valid_yaml(tmp_path: Path):
    yaml_content = """
    checks:
      - id: check1
        checker: reachability
      - id: check2
        checker: kernel_routes
    """
    file_path = tmp_path / "evaluation-plan.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    result = EvaluationPlanValidator.validate(file_path)
    assert result.valid is True
    assert len(result.errors) == 0


def test_validator_missing_checks_key(tmp_path: Path):
    yaml_content = """
    some_other_key:
      - id: check1
    """
    file_path = tmp_path / "evaluation-plan.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    result = EvaluationPlanValidator.validate(file_path)
    assert result.valid is False
    assert any("Manca la chiave 'checks'" in e for e in result.errors)


def test_validator_checks_is_not_list(tmp_path: Path):
    yaml_content = """
    checks:
      id: check1
      checker: reachability
    """
    file_path = tmp_path / "evaluation-plan.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    result = EvaluationPlanValidator.validate(file_path)
    assert result.valid is False
    assert any("deve essere una lista" in e for e in result.errors)


def test_validator_missing_id_and_checker(tmp_path: Path):
    yaml_content = """
    checks:
      - some_field: value
    """
    file_path = tmp_path / "evaluation-plan.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    result = EvaluationPlanValidator.validate(file_path)
    assert result.valid is False
    assert any("Manca o invalido 'id'" in e for e in result.errors)
    assert any("Manca o invalido 'checker'" in e for e in result.errors)


def test_validator_duplicate_id(tmp_path: Path):
    yaml_content = """
    checks:
      - id: check1
        checker: reachability
      - id: check1
        checker: something_else
    """
    file_path = tmp_path / "evaluation-plan.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    result = EvaluationPlanValidator.validate(file_path)
    assert result.valid is False
    assert any("ID duplicato: check1" in e for e in result.errors)


def test_validator_placeholders(tmp_path: Path):
    yaml_content = """
    checks:
      - id: check1
        checker: reachability
        target: <placeholder>
    """
    file_path = tmp_path / "evaluation-plan.yaml"
    file_path.write_text(yaml_content, encoding="utf-8")

    result = EvaluationPlanValidator.validate(file_path)
    assert result.valid is False
    assert any("Rilevato placeholder '<placeholder>'" in e for e in result.errors)
