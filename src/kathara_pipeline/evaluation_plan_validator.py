from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class EvaluationPlanValidationResult:
    valid: bool
    errors: tuple[str, ...]


class EvaluationPlanValidator:
    """Minimal validator for evaluation-plan.yaml.
    
    Ensures structural integrity without duplicating the full checker semantic validation.
    """

    @classmethod
    def validate(cls, path: Path) -> EvaluationPlanValidationResult:
        if not path.is_file():
            return EvaluationPlanValidationResult(False, (f"File non trovato: {path}",))

        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            return EvaluationPlanValidationResult(False, (f"Impossibile parsare YAML: {exc}",))

        if not isinstance(data, dict):
            return EvaluationPlanValidationResult(False, ("Il documento YAML deve essere un dizionario.",))

        errors: list[str] = []

        # checks key must exist and be a list
        if "checks" not in data:
            errors.append("Manca la chiave 'checks'.")
        elif not isinstance(data["checks"], list):
            errors.append("La chiave 'checks' deve essere una lista.")
        else:
            checks = data["checks"]
            seen_ids = set()

            for i, check in enumerate(checks):
                if not isinstance(check, dict):
                    errors.append(f"Il check all'indice {i} non è un dizionario.")
                    continue

                check_id = check.get("id")
                if not check_id or not isinstance(check_id, str):
                    errors.append(f"Manca o invalido 'id' per il check all'indice {i}.")
                else:
                    if check_id in seen_ids:
                        errors.append(f"ID duplicato: {check_id}")
                    seen_ids.add(check_id)

                checker = check.get("checker")
                if not checker or not isinstance(checker, str):
                    errors.append(f"Manca o invalido 'checker' (primitive/category) per il check all'indice {i}.")

        # Check for placeholders anywhere in the document
        cls._check_placeholders(path, errors)

        return EvaluationPlanValidationResult(valid=len(errors) == 0, errors=tuple(errors))

    @classmethod
    def _check_placeholders(cls, path: Path, errors: list[str]) -> None:
        raw_text = path.read_text(encoding="utf-8")
        placeholders = ["TODO", "...", "<placeholder>", "[placeholder]", "<da_inserire>"]
        for p in placeholders:
            if p in raw_text:
                errors.append(f"Rilevato placeholder '{p}' nel file.")
