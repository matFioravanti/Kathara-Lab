import io
import pytest
from kathara_pipeline.console import PipelineConsole

def test_pipeline_started():
    stream = io.StringIO()
    console = PipelineConsole(stream)
    console.pipeline_started("Codex CLI", "GPT-5.6 Sol", "light", 3)
    output = stream.getvalue()
    
    assert "Kathara-Lab Pipeline" in output
    assert "Provider: Codex CLI" in output
    assert "Model: GPT-5.6 Sol" in output
    assert "Reasoning: light" in output
    assert "Prompt trovati: 3" in output

def test_experiment_started():
    stream = io.StringIO()
    console = PipelineConsole(stream)
    
    console.experiment_started("first_prompt", 1, 3)
    assert "[1/3] first_prompt" in stream.getvalue()
    
    stream = io.StringIO()
    console = PipelineConsole(stream)
    console.experiment_started("second_prompt", 2, 3)
    output = stream.getvalue()
    assert output.startswith("\n[2/3] second_prompt")

def test_phase_success():
    stream = io.StringIO()
    console = PipelineConsole(stream)
    console.phase_started("Generazione laboratorio", 1, 6)
    console.phase_success("Laboratorio generato")
    
    output = stream.getvalue()
    assert "  [1/6] Generazione laboratorio..." in output
    assert "        ✓ Laboratorio generato" in output

def test_checker_attempted_not_completed():
    stream = io.StringIO()
    console = PipelineConsole(stream)
    console.phase_started("Checker", 5, 6)
    console.checker_started()
    console.checker_failed("container crashed")
    
    output = stream.getvalue()
    assert "        ✓ Checker avviato" in output
    assert "        ✗ Checker non completato" in output
    assert "          Error: container crashed" in output

def test_checker_completed():
    stream = io.StringIO()
    console = PipelineConsole(stream)
    console.checker_started()
    console.checker_completed()
    console.checker_metrics(24, 19, 5, 79.17)
    
    output = stream.getvalue()
    assert "        ✓ Checker avviato" in output
    assert "        ✓ Checker completato" in output
    assert "        Test: 24 | Passed: 19 | Failed: 5 | Pass: 79.17%" in output

def test_phase_error():
    stream = io.StringIO()
    console = PipelineConsole(stream)
    console.phase_failure("Generazione evaluation-spec.md fallita", "network error")
    
    output = stream.getvalue()
    assert "        ✗ Generazione evaluation-spec.md fallita" in output
    assert "          Error: network error" in output
