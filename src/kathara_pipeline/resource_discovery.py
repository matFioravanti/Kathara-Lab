from __future__ import annotations

from pathlib import Path

from .exceptions import ResourceError
from .models import ResourceFiles
from .state_store import sha256_file


def discover_resources(resources_root: Path) -> ResourceFiles:
    root = Path(resources_root).expanduser().resolve(strict=False)
    creation = root / "skills" / "creation" / "SKILL.md"
    checker = root / "skills" / "checker" / "SKILL.md"
    schema = root / "checker" / "config-schema.md"
    missing = [str(path) for path in (creation, checker, schema) if not path.is_file() or path.is_symlink()]
    if missing:
        raise ResourceError("Risorse framework mancanti: " + ", ".join(missing))
    return ResourceFiles(
        root=root,
        creation_skill=creation,
        checker_skill=checker,
        checker_schema=schema,
        creation_skill_hash=sha256_file(creation),
        checker_skill_hash=sha256_file(checker),
        checker_schema_hash=sha256_file(schema),
    )
