from pathlib import Path
from kathara_pipeline.codex_runner import CodexRunner
from kathara_pipeline.gemini_runner import GeminiRunner
from kathara_pipeline.claude_runner import ClaudeRunner


def test_codex_keeps_model_reasoning_and_sandbox(tmp_path: Path):
    cmd = CodexRunner("codex", "gpt-5.6-terra", "low", "workspace-write").build_command(instruction="x", workspace=tmp_path, output_last_message=tmp_path/"last")
    assert "gpt-5.6-terra" in cmd
    assert 'model_reasoning_effort="low"' in cmd
    assert 'approval_policy="never"' in cmd
    assert "workspace-write" in cmd


def test_gemini_and_claude_headless_commands(tmp_path: Path):
    g = GeminiRunner("gemini", "auto", "workspace-write").build_command(instruction="x", workspace=tmp_path, output_last_message=tmp_path/"x")
    c = ClaudeRunner("claude", "sonnet", "low").build_command(instruction="x", workspace=tmp_path, output_last_message=tmp_path/"x")
    assert "--prompt" in g and "stream-json" in g
    assert "--print" in c and "--safe-mode" in c and "--no-session-persistence" in c and "Read,Write,Edit" in c
