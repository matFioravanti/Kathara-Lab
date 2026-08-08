from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from kathara_pipeline.codex_runner import CodexRunner
from kathara_pipeline.correction_generator import CorrectionGenerator
from kathara_pipeline.exceptions import (
    CodexAuthenticationError,
    CodexExecutionError,
    CodexSignalError,
    CorrectionGenerationError,
    LabGenerationError,
)
from kathara_pipeline.lab_generator import LabGenerator
from kathara_pipeline.models import CommandResult, PromptRecord, ResourceFiles
from kathara_pipeline.paths import build_job_paths, ensure_generated_root_managed


def test_build_command_uses_confirmed_exec_local_flags(tmp_path: Path) -> None:
    runner = CodexRunner(command="codex-custom", timeout_seconds=9)
    command = runner.build_command(
        workspace=tmp_path,
        output_last_message=tmp_path / "last.txt",
        instruction="Generate the lab",
    )

    assert command == [
        "codex-custom",
        "exec",
        "--model",
        "gpt-5.6-terra",
        "-c",
        'model_reasoning_effort="low"',
        "-c",
        'approval_policy="never"',
        "--sandbox",
        "workspace-write",
        "--cd",
        str(tmp_path),
        "--json",
        "--output-last-message",
        str(tmp_path / "last.txt"),
        "--ephemeral",
        "Generate the lab",
    ]
    assert "--ask-for-approval" not in command
    assert "--dangerously-bypass-approvals-and-sandbox" not in command
    assert "--yolo" not in command


def test_run_invokes_once_and_keeps_jsonl_and_stderr_separate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    final_message = workspace / "last.txt"
    calls: list[tuple[list[str], dict[str, object]]] = []
    stdout = (
        '{"type":"thread.started"}\n'
        "malformed event\n"
        '{"type":"turn.completed","usage":{}}\n'
    )

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        final_message.write_text("done", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="path warning\n")

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    jsonl_log = tmp_path / "logs" / "codex.jsonl"
    stderr_log = tmp_path / "logs" / "codex.stderr.log"
    result = CodexRunner(timeout_seconds=12).run(
        instruction="Generate",
        workspace=workspace,
        output_last_message=final_message,
        jsonl_log=jsonl_log,
        stderr_log=stderr_log,
    )

    assert len(calls) == 1
    command, kwargs = calls[0]
    assert isinstance(command, list)
    assert kwargs["shell"] is False
    assert kwargs["timeout"] == 12
    assert result.malformed_json_lines == (2,)
    assert jsonl_log.read_text(encoding="utf-8") == stdout
    assert stderr_log.read_text(encoding="utf-8") == "path warning\n"


def test_run_rejects_stream_without_completed_turn_and_retains_logs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    final_message = workspace / "last.txt"

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        final_message.write_text("unfinished", encoding="utf-8")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout='{"type":"turn.started"}\nnot-json\n',
            stderr="diagnostic",
        )

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    jsonl_log = tmp_path / "codex.jsonl"
    stderr_log = tmp_path / "codex.stderr"
    with pytest.raises(CodexExecutionError, match="turn.completed") as captured:
        CodexRunner().run(
            instruction="Generate",
            workspace=workspace,
            output_last_message=final_message,
            jsonl_log=jsonl_log,
            stderr_log=stderr_log,
        )
    assert "not-json" in jsonl_log.read_text(encoding="utf-8")
    assert stderr_log.read_text(encoding="utf-8") == "diagnostic"
    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["return_code"] == 0
    assert metadata["timed_out"] is False
    assert metadata["malformed_json_lines"] == [2]
    assert metadata["cwd"] == str(workspace)
    assert metadata["jsonl_log"] == str(jsonl_log)
    assert metadata["stderr_log"] == str(stderr_log)
    assert metadata["command"][-1] == "<instruction>"


def test_codex_logs_redact_common_secret_forms(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    final_message = workspace / "last.txt"

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        final_message.write_text("done", encoding="utf-8")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout='{"type":"turn.completed","note":"sk-abcdefghijklmnop"}\n',
            stderr="Authorization: Bearer very-secret-value",
        )

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    jsonl_log = tmp_path / "codex.jsonl"
    stderr_log = tmp_path / "codex.stderr"

    CodexRunner().run(
        instruction="Generate",
        workspace=workspace,
        output_last_message=final_message,
        jsonl_log=jsonl_log,
        stderr_log=stderr_log,
    )

    assert "sk-abcdefghijklmnop" not in jsonl_log.read_text(encoding="utf-8")
    assert "very-secret-value" not in stderr_log.read_text(encoding="utf-8")


def test_run_timeout_is_an_error_and_writes_partial_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(
            command,
            timeout=3,
            output=b'{"type":"turn.started"}\n',
            stderr=b"timeout details",
        )

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    stdout_log = tmp_path / "stdout.jsonl"
    stderr_log = tmp_path / "stderr.log"
    with pytest.raises(CodexExecutionError, match="timed out") as captured:
        CodexRunner(timeout_seconds=3).run(
            instruction="Generate",
            workspace=workspace,
            output_last_message=workspace / "last.txt",
            jsonl_log=stdout_log,
            stderr_log=stderr_log,
        )
    assert "turn.started" in stdout_log.read_text(encoding="utf-8")
    assert stderr_log.read_text(encoding="utf-8") == "timeout details"
    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["return_code"] is None
    assert metadata["timed_out"] is True
    assert metadata["malformed_json_lines"] == []


def test_run_nonzero_return_is_error_and_is_not_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    calls = 0

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            command,
            4,
            stdout='{"type":"turn.failed"}\n',
            stderr="authentication expired",
        )

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    with pytest.raises(CodexAuthenticationError, match="authentication") as captured:
        CodexRunner().run(
            instruction="Generate",
            workspace=workspace,
            output_last_message=workspace / "last.txt",
            jsonl_log=tmp_path / "stdout.jsonl",
            stderr_log=tmp_path / "stderr.log",
        )
    assert calls == 1
    assert "authentication expired" in (tmp_path / "stderr.log").read_text(encoding="utf-8")
    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["return_code"] == 4
    assert metadata["timed_out"] is False
    assert metadata["command"][-1] == "<instruction>"


def test_run_classifies_signal_termination_and_keeps_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, -15, stdout="", stderr="terminated")

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    with pytest.raises(CodexSignalError, match="signal 15") as captured:
        CodexRunner().run(
            instruction="Generate",
            workspace=workspace,
            output_last_message=workspace / "last.txt",
            jsonl_log=tmp_path / "stdout.jsonl",
            stderr_log=tmp_path / "stderr.log",
        )

    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["return_code"] == -15
    assert metadata["timed_out"] is False


def test_run_file_not_found_is_explicit_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError(command[0])

    monkeypatch.setattr("kathara_pipeline.codex_runner.subprocess.run", fake_run)
    with pytest.raises(CodexExecutionError, match="command not found"):
        CodexRunner(command="missing-codex").run(
            instruction="Generate",
            workspace=workspace,
            output_last_message=workspace / "last.txt",
            jsonl_log=tmp_path / "stdout.jsonl",
            stderr_log=tmp_path / "stderr.log",
        )
    assert "missing-codex" in (tmp_path / "stderr.log").read_text(encoding="utf-8")


def test_run_rejects_final_message_outside_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with pytest.raises(CodexExecutionError, match="inside"):
        CodexRunner().run(
            instruction="Generate",
            workspace=workspace,
            output_last_message=tmp_path / "outside.txt",
            jsonl_log=tmp_path / "stdout.jsonl",
            stderr_log=tmp_path / "stderr.log",
        )


class _GeneratingRunner:
    def __init__(self, phase: str) -> None:
        self.phase = phase
        self.calls = 0

    def run(self, **kwargs: object) -> CommandResult:
        self.calls += 1
        workspace = Path(str(kwargs["workspace"]))
        final_message = Path(str(kwargs["output_last_message"]))
        final_message.write_text("done", encoding="utf-8")
        if self.phase == "lab":
            (workspace / "output" / "lab" / "lab.conf").write_text(
                'r1[0]="A"\n', encoding="utf-8"
            )
        else:
            (workspace / "output" / "correction.yaml").write_text(
                "default_image: kathara/base\nlab_inline: |\n  r1[0]=\"A\"\ntest: {}\n",
                encoding="utf-8",
            )
        return CommandResult(("codex", "exec"), 0, "", "", 0.1)


def test_generators_each_use_one_codex_turn_and_collect_only_expected_output(
    tmp_path: Path,
) -> None:
    generated_root = tmp_path / "generated"
    ensure_generated_root_managed(generated_root, initialize=True)
    paths = build_job_paths(generated_root, "lab-1")
    paths.logs.mkdir(parents=True)
    prompt = PromptRecord(
        path=tmp_path / "lab-1.md",
        name="lab-1.md",
        lab_id="lab-1",
        content="Create one router",
        prompt_hash="abc",
    )
    lab_runner = _GeneratingRunner("lab")
    LabGenerator(lab_runner).generate(prompt, paths)  # type: ignore[arg-type]
    assert lab_runner.calls == 1
    assert (paths.source / "lab.conf").is_file()
    assert not paths.lab_workspace.exists()

    skill = tmp_path / "SKILL.md"
    schema = tmp_path / "config-schema.json"
    skill.write_text("Skill", encoding="utf-8")
    schema.write_text("{}", encoding="utf-8")
    resources = ResourceFiles(
        root=tmp_path,
        skill_path=skill,
        schema_path=schema,
        examples_path=None,
        skill_hash="skill",
        schema_hash="schema",
        schema_mode="json-schema",
    )
    correction_runner = _GeneratingRunner("correction")
    CorrectionGenerator(correction_runner).generate(  # type: ignore[arg-type]
        prompt, paths, resources
    )
    assert correction_runner.calls == 1
    assert paths.correction.name == "correction.yaml"
    assert paths.correction.is_file()
    assert not paths.correction_workspace.exists()


class _SuccessfulResultOnlyRunner:
    def run(self, **kwargs: object) -> CommandResult:
        final_message = Path(str(kwargs["output_last_message"]))
        final_message.write_text("done", encoding="utf-8")
        return CommandResult(
            ("codex", "exec", "instruction containing sk-abcdefghijklmnop"),
            0,
            "",
            "",
            0.3,
            malformed_json_lines=(4,),
        )


def test_lab_post_run_validation_error_retains_codex_process_metadata(tmp_path: Path) -> None:
    generated_root = tmp_path / "generated"
    ensure_generated_root_managed(generated_root, initialize=True)
    paths = build_job_paths(generated_root, "lab-1")
    paths.logs.mkdir(parents=True)
    prompt = PromptRecord(
        path=tmp_path / "lab-1.md",
        name="lab-1.md",
        lab_id="lab-1",
        content="Create one router",
        prompt_hash="abc",
    )

    with pytest.raises(LabGenerationError, match="empty laboratory") as captured:
        LabGenerator(_SuccessfulResultOnlyRunner()).generate(prompt, paths)  # type: ignore[arg-type]

    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["command"][-1] == "<instruction>"
    assert metadata["return_code"] == 0
    assert metadata["duration_seconds"] == pytest.approx(0.3)
    assert metadata["timed_out"] is False
    assert metadata["cwd"] == str(paths.lab_workspace)
    assert metadata["jsonl_log"] == str(paths.logs / "codex-lab.jsonl")
    assert metadata["malformed_json_lines"] == [4]


def test_correction_post_run_validation_error_retains_codex_process_metadata(
    tmp_path: Path,
) -> None:
    generated_root = tmp_path / "generated"
    ensure_generated_root_managed(generated_root, initialize=True)
    paths = build_job_paths(generated_root, "lab-1")
    paths.source.mkdir(parents=True)
    (paths.source / "lab.conf").write_text('r1[0]="A"\n', encoding="utf-8")
    paths.logs.mkdir(parents=True)
    prompt = PromptRecord(
        path=tmp_path / "lab-1.md",
        name="lab-1.md",
        lab_id="lab-1",
        content="Create one router",
        prompt_hash="abc",
    )
    skill = tmp_path / "SKILL.md"
    schema = tmp_path / "config-schema.json"
    skill.write_text("Skill", encoding="utf-8")
    schema.write_text("{}", encoding="utf-8")
    resources = ResourceFiles(
        root=tmp_path,
        skill_path=skill,
        schema_path=schema,
        examples_path=None,
        skill_hash="skill",
        schema_hash="schema",
        schema_mode="json-schema",
    )

    with pytest.raises(CorrectionGenerationError, match="did not create") as captured:
        CorrectionGenerator(_SuccessfulResultOnlyRunner()).generate(  # type: ignore[arg-type]
            prompt, paths, resources
        )

    metadata = captured.value.process_metadata
    assert metadata is not None
    assert metadata["command"][-1] == "<instruction>"
    assert metadata["return_code"] == 0
    assert metadata["cwd"] == str(paths.correction_workspace)
    assert metadata["jsonl_log"] == str(paths.logs / "codex-correction.jsonl")
    assert metadata["stderr_log"] == str(paths.logs / "codex-correction.stderr.log")
