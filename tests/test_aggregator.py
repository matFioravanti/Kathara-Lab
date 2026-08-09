from kathara_pipeline.models import ComparisonOutcome, ExperimentSummary, JobStatus, Variant, VariantSummary
from kathara_pipeline.report_aggregator import aggregate_payload


def test_aggregate_keeps_quality_and_technical_metrics_separate():
    a = VariantSummary("e", "p", Variant.WITH_SKILL, JobStatus.PASSED, checker_completed=True, total_tests=10, passed_tests=10, failed_tests=0, pass_percentage=100.0, generation_duration_seconds=4)
    b = VariantSummary("e", "p", Variant.WITHOUT_SKILL, JobStatus.FAILED, checker_completed=True, total_tests=10, passed_tests=8, failed_tests=2, pass_percentage=80.0, generation_duration_seconds=3)
    data = aggregate_payload([ExperimentSummary("e", "p", True, True, "hash", a, b, ComparisonOutcome.WITH_SKILL_BETTER, "x")])
    assert data["quality"]["paired"]["mean_delta_pass_percentage_points"] == 20.0
    assert data["technical_reliability"]["with_skill_errors"] == 0
