from __future__ import annotations

from pathlib import Path

import pytest

from kathara_pipeline.exceptions import PromptDiscoveryError, UnsafePathError
from kathara_pipeline.models import PromptRecord
from kathara_pipeline.paths import (
    GENERATED_ROOT_MARKER,
    GENERATED_ROOT_MARKER_CONTENT,
    build_job_paths,
    detect_lab_id_collisions,
    ensure_generated_root_managed,
    ensure_no_lab_id_collisions,
    lab_id_from_prompt,
    paths_overlap,
    safe_rmtree,
    sanitize_lab_id,
)


def _managed_root(root: Path) -> None:
    ensure_generated_root_managed(root, initialize=True)


def _record(path: Path, lab_id: str) -> PromptRecord:
    return PromptRecord(
        path=path,
        name=path.name,
        lab_id=lab_id,
        content="prompt",
        prompt_hash="hash",
    )


def test_lab_id_is_derived_from_filename_stem() -> None:
    assert lab_id_from_prompt(Path("prompt_still_to_be_generated/lab-001-v1.md")) == "lab-001-v1"


def test_lab_id_sanitizes_portable_non_path_characters() -> None:
    assert sanitize_lab_id("  Réseau @ 01  ") == "Reseau-01"


@pytest.mark.parametrize(
    "raw_name",
    ["", "   ", ".", "..", "../outside", r"..\outside", "bad\nname", "CON", "nul.txt"],
)
def test_lab_id_rejects_unsafe_names(raw_name: str) -> None:
    with pytest.raises(UnsafePathError):
        sanitize_lab_id(raw_name)


def test_collision_detection_lists_distinct_prompt_paths(tmp_path: Path) -> None:
    prompts = [
        _record(tmp_path / "lab a.md", "lab-a"),
        _record(tmp_path / "lab@a.txt", "lab-a"),
        _record(tmp_path / "other.md", "other"),
    ]

    collisions = detect_lab_id_collisions(prompts)

    assert collisions == {
        "lab-a": (tmp_path / "lab a.md", tmp_path / "lab@a.txt"),
    }
    with pytest.raises(PromptDiscoveryError, match="lab a.md"):
        ensure_no_lab_id_collisions(prompts)


def test_collision_detection_is_case_insensitive_for_portable_output_paths(
    tmp_path: Path,
) -> None:
    prompts = [
        _record(tmp_path / "Foo!.md", "Foo"),
        _record(tmp_path / "foo?.txt", "foo"),
    ]

    assert detect_lab_id_collisions(prompts) == {
        "Foo / foo": (tmp_path / "Foo!.md", tmp_path / "foo?.txt"),
    }
    with pytest.raises(PromptDiscoveryError, match="Foo / foo"):
        ensure_no_lab_id_collisions(prompts)


def test_overlap_detects_case_alias_for_not_yet_created_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inputs = tmp_path / "prompt_still_to_be_generated"
    inputs.mkdir()
    output = tmp_path / "PROMPT_STILL_TO_BE_GENERATED" / "generated"

    monkeypatch.setattr(
        "kathara_pipeline.paths._filesystem_is_case_insensitive", lambda _path: True
    )

    assert paths_overlap(output, inputs)


def test_build_job_paths_matches_canonical_layout(tmp_path: Path) -> None:
    generated_root = tmp_path / "kathara-lab-generates"

    paths = build_job_paths(generated_root, "lab-001")

    root = generated_root.resolve() / "lab-001"
    assert paths.root == root
    assert paths.prompt == root / "prompt.md"
    assert paths.source == root / "source"
    assert paths.correction == root / "correction" / "correction.yaml"
    assert paths.candidate == root / "checker-run" / "labs" / "candidate"
    assert paths.reports == root / "reports"
    assert paths.logs == root / "logs"
    assert paths.manifest == root / "manifest.json"
    assert paths.lab_workspace == root / ".workspaces" / "lab"
    assert paths.correction_workspace == root / ".workspaces" / "correction"


def test_safe_rmtree_removes_only_nested_generated_directory(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "kathara-lab-generates"
    _managed_root(generated_root)
    target = generated_root / "lab-001" / "checker-run"
    target.mkdir(parents=True)
    (target / "result.csv").write_text("result", encoding="utf-8")

    safe_rmtree(
        target,
        generated_root,
        project_root=project_root,
        home=tmp_path / "home",
    )

    assert not target.exists()
    assert generated_root.exists()


def test_safe_rmtree_missing_nested_directory_is_noop(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "kathara-lab-generates"
    generated_root.mkdir(parents=True)
    _managed_root(generated_root)

    safe_rmtree(
        generated_root / "lab-001" / "missing",
        generated_root,
        project_root=project_root,
        home=tmp_path / "home",
    )


def test_safe_rmtree_refuses_generated_root_itself(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "kathara-lab-generates"
    generated_root.mkdir(parents=True)
    _managed_root(generated_root)

    with pytest.raises(UnsafePathError, match="interezza"):
        safe_rmtree(
            generated_root,
            generated_root,
            project_root=project_root,
            home=tmp_path / "home",
        )
    assert generated_root.exists()


def test_safe_rmtree_refuses_path_traversal_outside_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "kathara-lab-generates"
    generated_root.mkdir(parents=True)
    _managed_root(generated_root)
    outside = project_root / "outside"
    outside.mkdir()

    with pytest.raises(UnsafePathError, match="esterno"):
        safe_rmtree(
            generated_root / ".." / "outside",
            generated_root,
            project_root=project_root,
            home=tmp_path / "home",
        )
    assert outside.exists()


def test_safe_rmtree_refuses_symlink_pointing_outside_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "kathara-lab-generates"
    generated_root.mkdir(parents=True)
    _managed_root(generated_root)
    outside = tmp_path / "outside"
    outside.mkdir()
    link = generated_root / "linked-job"
    link.symlink_to(outside, target_is_directory=True)

    with pytest.raises(UnsafePathError):
        safe_rmtree(
            link,
            generated_root,
            project_root=project_root,
            home=tmp_path / "home",
        )
    assert link.is_symlink()
    assert outside.exists()


def test_safe_rmtree_refuses_regular_file(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "kathara-lab-generates"
    generated_root.mkdir(parents=True)
    _managed_root(generated_root)
    target = generated_root / "manifest.json"
    target.write_text("{}", encoding="utf-8")

    with pytest.raises(UnsafePathError, match="non è una directory"):
        safe_rmtree(
            target,
            generated_root,
            project_root=project_root,
            home=tmp_path / "home",
        )
    assert target.exists()


def test_generated_root_marker_is_initialized_only_for_missing_or_empty_roots(tmp_path: Path) -> None:
    root = tmp_path / "generated"

    ensure_generated_root_managed(root, initialize=False)
    assert not root.exists()
    ensure_generated_root_managed(root, initialize=True)

    marker = root / GENERATED_ROOT_MARKER
    assert marker.is_file()
    assert marker.read_text(encoding="utf-8") == GENERATED_ROOT_MARKER_CONTENT


def test_marker_write_failure_leaves_empty_root_retryable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "generated"

    with monkeypatch.context() as context:
        context.setattr(
            "kathara_pipeline.paths.os.replace",
            lambda _source, _destination: (_ for _ in ()).throw(OSError("disk full")),
        )
        with pytest.raises(OSError, match="disk full"):
            ensure_generated_root_managed(root, initialize=True)

    assert root.is_dir()
    assert list(root.iterdir()) == []
    assert not any(path.name.startswith(".generated.marker-") for path in tmp_path.iterdir())

    ensure_generated_root_managed(root, initialize=True)
    assert (root / GENERATED_ROOT_MARKER).read_text(encoding="utf-8") == (
        GENERATED_ROOT_MARKER_CONTENT
    )


def test_generated_root_rejects_nonempty_root_without_valid_regular_marker(tmp_path: Path) -> None:
    root = tmp_path / "generated"
    root.mkdir()
    (root / "user-file.txt").write_text("do not delete", encoding="utf-8")

    with pytest.raises(UnsafePathError, match="non è gestita"):
        ensure_generated_root_managed(root, initialize=True)

    marker = root / GENERATED_ROOT_MARKER
    marker.write_text(GENERATED_ROOT_MARKER_CONTENT, encoding="utf-8")
    marker.unlink()
    marker.symlink_to(root / "user-file.txt")
    with pytest.raises(UnsafePathError, match="marker regolare"):
        ensure_generated_root_managed(root, initialize=False)


def test_safe_rmtree_requires_managed_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    generated_root = project_root / "generated"
    target = generated_root / "job"
    target.mkdir(parents=True)

    with pytest.raises(UnsafePathError, match="non è gestita"):
        safe_rmtree(target, generated_root, project_root=project_root, home=tmp_path / "home")
    assert target.exists()


def test_safe_rmtree_rejects_intermediate_symlink_inserted_after_path_selection(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside = tmp_path / "outside"
    generated_outside = outside / "generated"
    ensure_generated_root_managed(generated_outside, initialize=True)
    target = generated_outside / "job"
    target.mkdir()
    (project_root / "build").symlink_to(outside, target_is_directory=True)
    configured_root = project_root / "build" / "generated"

    with pytest.raises(UnsafePathError, match="symlink|esterna al progetto"):
        safe_rmtree(
            configured_root / "job",
            configured_root,
            project_root=project_root,
            home=tmp_path / "home",
        )

    assert target.is_dir()
