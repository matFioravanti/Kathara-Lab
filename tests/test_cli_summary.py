import io
import pytest
from unittest.mock import patch, MagicMock
from kathara_pipeline.cli import main
from kathara_pipeline.models import PipelineSummary

@patch("kathara_pipeline.cli.Pipeline")
def test_no_final_summary_on_run(mock_pipeline_class, monkeypatch):
    mock_pipeline = MagicMock()
    mock_pipeline_class.return_value = mock_pipeline
    
    mock_summary = MagicMock(spec=PipelineSummary)
    mock_summary.experiments = []
    mock_pipeline.run.return_value = mock_summary
    
    # Mock discover and preflight
    mock_pipeline.discover.return_value = []
    mock_preflight_result = MagicMock()
    mock_preflight_result.warnings = []
    mock_pipeline.preflight.return_value = mock_preflight_result
    
    stream = io.StringIO()
    monkeypatch.setattr("sys.stdout", stream)
    
    # Execute the run command
    ret = main(["run", "--prompts-dir", "dummy"])
    assert ret == 0
        
    output = stream.getvalue()
    
    # The console should be initialized inside main and pipeline_started called
    # But we mocked Pipeline. We just want to ensure "_print_summary" was bypassed.
    assert "Riepilogo esperimento:" not in output
