from pathlib import Path

from kathara_pipeline.lab_validator import LabValidator


def _lab(root: Path) -> Path:
    lab = root / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text('r1[0]="A"\nr2[0]="A"\n', encoding="utf-8")
    (lab / "r1.startup").write_text("ip addr replace 10.0.0.1/24 dev eth0\n", encoding="utf-8")
    (lab / "r2.startup").write_text("ip addr replace 10.0.0.2/24 dev eth0\n", encoding="utf-8")
    return lab


def test_prompt_text_is_ignored(tmp_path: Path):
    lab = _lab(tmp_path)
    prompt = """
    Create the file /etc/frr/frr.conf for r1.
    Use the Skill.md in the kathara-lab-creation folder as a guide.
    Addresses are `192.168.1.1`, `.1`, `.10`, 10.0.0.1/24,
    2001:db8::1 and version 1.10.
    """
    # Even if the prompt asks for frr.conf, LabValidator no longer parses the prompt
    # and only checks the structural validity of the lab. The lab is structurally valid.
    result = LabValidator().validate(lab, prompt)
    assert result.valid, result.errors


def test_undeclared_startup_is_structural_error(tmp_path: Path):
    lab = _lab(tmp_path)
    (lab / "ghost.startup").write_text("echo x\n", encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("undeclared device" in e for e in result.errors)


def test_missing_lab_conf_is_error(tmp_path: Path):
    lab = tmp_path / "lab"
    lab.mkdir()
    assert not LabValidator().validate(lab).valid

def test_valid_collision_domain(tmp_path: Path):
    lab = tmp_path / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text('r1[0]="r1_r2"\nr2[0]="r1_r2"\n', encoding="utf-8")
    result = LabValidator().validate(lab)
    assert result.valid

def test_invalid_collision_domain_with_hyphen(tmp_path: Path):
    lab = tmp_path / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text('r1[0]="r1-r2"\nr2[0]="r1-r2"\n', encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("LabParser validation failed" in e for e in result.errors)

def test_invalid_device_identifier(tmp_path: Path):
    lab = tmp_path / "lab"
    lab.mkdir()
    (lab / "lab.conf").write_text('r1-x[0]="A"\n', encoding="utf-8")
    result = LabValidator().validate(lab)
    assert not result.valid
    assert any("LabParser validation failed" in e for e in result.errors)
