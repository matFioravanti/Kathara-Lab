from pathlib import Path

from kathara_pipeline.prompt_discovery import discover_prompts


def test_external_prompt_directory_is_read_only_and_natural_sorted(tmp_path: Path):
    prompts = tmp_path / "input-prompts"
    prompts.mkdir()
    (prompts / "lab10.md").write_text("ten", encoding="utf-8")
    (prompts / "lab2.md").write_text("two", encoding="utf-8")
    (prompts / "ignore.bin").write_bytes(b"x")
    before = sorted(p.name for p in prompts.iterdir())
    records = discover_prompts(prompts)
    assert [r.name for r in records] == ["lab2.md", "lab10.md"]
    assert sorted(p.name for p in prompts.iterdir()) == before


def test_prompt_names_with_spaces_commas_parentheses_and_accents_get_safe_ids(tmp_path: Path):
    prompts = tmp_path / "input-prompts"
    prompts.mkdir()
    (prompts / "All Routes Explicit, No Default Routes, IPv4.md").write_text("x", encoding="utf-8")
    (prompts / "Topologia (versione A) - città.md").write_text("y", encoding="utf-8")

    records = discover_prompts(prompts)

    assert records[0].experiment_id == "All_Routes_Explicit_No_Default_Routes_IPv4"
    assert records[1].experiment_id == "Topologia_versione_A_-_citta"
    assert all("/" not in r.experiment_id and "\\" not in r.experiment_id for r in records)


def test_normalized_experiment_id_collisions_are_resolved_deterministically(tmp_path: Path):
    prompts = tmp_path / "input-prompts"
    prompts.mkdir()
    (prompts / "Lab A.md").write_text("one", encoding="utf-8")
    (prompts / "Lab, A.md").write_text("two", encoding="utf-8")

    first = discover_prompts(prompts)
    second = discover_prompts(prompts)

    first_ids = [r.experiment_id for r in first]
    assert len(first_ids) == len(set(i.casefold() for i in first_ids)) == 2
    assert first_ids == [r.experiment_id for r in second]
