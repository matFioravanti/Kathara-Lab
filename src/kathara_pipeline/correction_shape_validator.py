from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any
from .models import ValidationResult

class CorrectionShapeValidator:
    """Validates that an adapted correction maintains the same structural shape as the reference."""
    
    @classmethod
    def validate(cls, reference_path: Path, adapted_path: Path) -> ValidationResult:
        try:
            with open(reference_path, 'r', encoding='utf-8') as f:
                ref_data = yaml.safe_load(f) or {}
            with open(adapted_path, 'r', encoding='utf-8') as f:
                adapt_data = yaml.safe_load(f) or {}
        except Exception as e:
            return ValidationResult(False, (f"Failed to parse YAML: {e}",))

        ref_shape = cls._extract_shape(ref_data.get('test', {}), depth=1)
        adapt_shape = cls._extract_shape(adapt_data.get('test', {}), depth=1)
        
        if ref_shape == adapt_shape:
            return ValidationResult(True, ())
        
        # If they don't match, we can provide a diff or generic error.
        errors = [
            "The adapted correction changed the structure of the reference correction.",
            "This is not allowed.",
            "Only candidate-dependent concrete values may differ.",
            "Please restore exactly the reference test structure and cardinality.",
        ]
        
        import json
        ref_str = json.dumps(ref_shape, sort_keys=True, indent=2)
        adapt_str = json.dumps(adapt_shape, sort_keys=True, indent=2)
        errors.append(f"Reference shape:\n{ref_str}")
        errors.append(f"Adapted shape:\n{adapt_str}")
        
        return ValidationResult(False, tuple(errors))

    @classmethod
    def _extract_shape(cls, data: Any, depth: int) -> Any:
        if isinstance(data, dict):
            if depth == 1:
                # Categories level (reachability, ping, etc.) -> keep keys
                return {k: cls._extract_shape(v, depth + 1) for k, v in data.items()}
            elif depth == 2:
                # Device instances level (pc1, routerA) -> anonymize keys
                # We sort the values' shapes to make it independent of key names
                shapes = [cls._extract_shape(v, depth + 1) for v in data.values()]
                
                # We need to sort shapes. Since they can be complex dicts/lists, we sort by string representation
                import json
                shapes.sort(key=lambda x: json.dumps(x, sort_keys=True))
                return shapes
            else:
                # Depth 3+
                # Some categories have dicts inside lists (e.g., custom_commands) where we want to keep keys.
                # Some have dicts inside dicts (e.g., dns_resolution) where keys might be domains.
                # To be safe and simple, we keep keys at depth 3+ but normalize all scalar values.
                return {k: cls._extract_shape(v, depth + 1) for k, v in data.items()}
        elif isinstance(data, list):
            shapes = [cls._extract_shape(v, depth + 1) for v in data]
            import json
            shapes.sort(key=lambda x: json.dumps(x, sort_keys=True))
            return shapes
        else:
            return "scalar"
