from __future__ import annotations

import json
from pathlib import Path

import pytest

from kathara_pipeline import state_store
from kathara_pipeline.exceptions import ManifestError
from kathara_pipeline.models import JobStatus
from kathara_pipeline.state_store import (
    StateStore,
    hash_directory,
    read_json,
    sha256_bytes,
    sha256_file,
    sha256_text,
    write_json_atomic,
)


def test_sha256_helpers_use_utf8_and_stream_files(tmp_path: Path) -> None:
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    path = tmp_path / "value.txt"
    path.write_bytes(b"abc")

    assert sha256_bytes(b"abc") == expected
    assert sha256_text("abc") == expected
    assert sha256_file(path, chunk_size=1) == expected


def test_sha256_file_rejects_nonpositive_chunk_size(tmp_path: Path) -> None:
    path = tmp_path / "value.txt"
    path.write_text("value", encoding="utf-8")

    with pytest.raises(ValueError, match="maggiore di zero"):
        sha256_file(path, chunk_size=0)


def test_hash_directory_is_relative_sorted_and_records_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "lab"
    (root / "device" / "etc").mkdir(parents=True)
    (root / "z.startup").write_text("z", encoding="utf-8")
    (root / "device" / "etc" / "config").write_text("config", encoding="utf-8")
    (root / "linked").symlink_to(root / "z.startup")

    hashes = hash_directory(root)

    assert list(hashes) == ["device/etc/config", "linked", "z.startup"]
    assert hashes["linked"] != hashes["z.startup"]
    assert hashes["z.startup"] == sha256_text("z")


def test_state_store_round_trip_is_atomic_and_serializes_common_types(tmp_path: Path) -> None:
    manifest = tmp_path / "job" / "manifest.json"
    store = StateStore(manifest)

    assert store.read() is None
    store.write(
        {
            "lab_id": "lab-001",
            "status": JobStatus.PASSED,
            "source": Path("source"),
            "accented": "verifica riuscita: sì",
        }
    )

    assert store.read() == {
        "accented": "verifica riuscita: sì",
        "lab_id": "lab-001",
        "source": "source",
        "status": "passed",
    }
    assert manifest.read_text(encoding="utf-8").endswith("\n")
    assert not list(manifest.parent.glob(f".{manifest.name}.*.tmp"))


def test_read_json_rejects_invalid_or_nonmapping_documents(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")
    with pytest.raises(ManifestError):
        read_json(invalid)

    sequence = tmp_path / "sequence.json"
    sequence.write_text(json.dumps([1, 2]), encoding="utf-8")
    with pytest.raises(ManifestError, match="oggetto JSON"):
        read_json(sequence)


def test_failed_atomic_replace_preserves_old_manifest_and_cleans_temp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = tmp_path / "manifest.json"
    write_json_atomic(manifest, {"status": "old"})

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr(state_store.os, "replace", fail_replace)

    with pytest.raises(ManifestError, match="atomicamente"):
        write_json_atomic(manifest, {"status": "new"})

    assert read_json(manifest) == {"status": "old"}
    assert not list(tmp_path.glob(f".{manifest.name}.*.tmp"))
