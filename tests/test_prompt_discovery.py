from __future__ import annotations

from pathlib import Path

import pytest

from kathara_pipeline.exceptions import PromptDiscoveryError
from kathara_pipeline.prompt_discovery import discover_prompts, natural_sort_key
from kathara_pipeline.state_store import sha256_bytes, sha256_text


def test_natural_sort_key_has_numeric_order_and_lexical_tiebreak() -> None:
    names = ["lab-10.md", "lab-2.md", "lab-001.md", "lab-1.md"]

    assert sorted(names, key=natural_sort_key) == [
        "lab-001.md",
        "lab-1.md",
        "lab-2.md",
        "lab-10.md",
    ]


def test_discovery_is_nonrecursive_filtered_and_naturally_sorted(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompt_still_to_be_generated"
    prompts_dir.mkdir()
    (prompts_dir / "lab-010-v1.md").write_text("ten", encoding="utf-8")
    (prompts_dir / "lab-002-v1.txt").write_text("two", encoding="utf-8")
    (prompts_dir / "lab-001-v1.MD").write_text("one", encoding="utf-8")
    (prompts_dir / ".hidden.md").write_text("hidden", encoding="utf-8")
    (prompts_dir / "ignored.json").write_text("{}", encoding="utf-8")
    nested = prompts_dir / "nested"
    nested.mkdir()
    (nested / "lab-000.md").write_text("nested", encoding="utf-8")

    records = discover_prompts(prompts_dir)

    assert [record.name for record in records] == [
        "lab-001-v1.MD",
        "lab-002-v1.txt",
        "lab-010-v1.md",
    ]
    assert [record.content for record in records] == ["one", "two", "ten"]
    assert records[0].prompt_hash == sha256_text("one")


def test_empty_and_whitespace_prompts_are_preserved(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompt_still_to_be_generated"
    prompts_dir.mkdir()
    (prompts_dir / "empty.md").write_bytes(b"")
    (prompts_dir / "whitespace.txt").write_text(" \n\t", encoding="utf-8")

    records = discover_prompts(prompts_dir)

    assert len(records) == 2
    assert all(record.empty for record in records)
    assert [record.content for record in records] == ["", " \n\t"]
    assert all(record.decode_error is None for record in records)


def test_utf8_error_is_a_record_and_does_not_block_later_prompt(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompt_still_to_be_generated"
    prompts_dir.mkdir()
    invalid_bytes = b"valid prefix\xffinvalid"
    (prompts_dir / "lab-1.md").write_bytes(invalid_bytes)
    (prompts_dir / "lab-2.md").write_text("valid prompt", encoding="utf-8")

    records = discover_prompts(prompts_dir)

    assert [record.name for record in records] == ["lab-1.md", "lab-2.md"]
    assert records[0].content is None
    assert "UTF-8" in (records[0].decode_error or "")
    assert records[0].prompt_hash == sha256_bytes(invalid_bytes)
    assert records[1].content == "valid prompt"
    assert records[1].decode_error is None


def test_sanitization_collision_aborts_discovery(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompt_still_to_be_generated"
    prompts_dir.mkdir()
    (prompts_dir / "lab a.md").write_text("first", encoding="utf-8")
    (prompts_dir / "lab@a.txt").write_text("second", encoding="utf-8")

    with pytest.raises(PromptDiscoveryError, match="Collisioni"):
        discover_prompts(prompts_dir)


def test_missing_prompt_directory_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(PromptDiscoveryError, match="inesistente"):
        discover_prompts(tmp_path / "missing")


def test_empty_directory_returns_empty_discovery(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompt_still_to_be_generated"
    prompts_dir.mkdir()

    assert discover_prompts(prompts_dir) == []


def test_prompt_symlink_is_rejected_instead_of_reading_external_content(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompt_still_to_be_generated"
    prompts_dir.mkdir()
    external = tmp_path / "external-secret.md"
    external.write_text("must not be read", encoding="utf-8")
    link = prompts_dir / "leak.md"
    try:
        link.symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported on this platform")

    with pytest.raises(PromptDiscoveryError, match="non symlink"):
        discover_prompts(prompts_dir)
