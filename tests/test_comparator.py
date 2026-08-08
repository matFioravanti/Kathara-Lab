from kathara_pipeline.comparator import compare_variants
from kathara_pipeline.models import ComparisonOutcome, JobStatus, Variant, VariantSummary


def _v(variant, failed, pct):
    return VariantSummary("x", "x.md", variant, JobStatus.FAILED if failed else JobStatus.PASSED, checker_completed=True, total_tests=10, passed_tests=10-failed, failed_tests=failed, pass_percentage=pct)


def test_pairwise_comparison_uses_same_checker_metrics():
    outcome, _ = compare_variants(_v(Variant.WITH_SKILL, 1, 90), _v(Variant.WITHOUT_SKILL, 3, 70))
    assert outcome is ComparisonOutcome.WITH_SKILL_BETTER


def test_pair_incomparable_if_test_count_differs():
    a = _v(Variant.WITH_SKILL, 1, 90)
    b = _v(Variant.WITHOUT_SKILL, 1, 90)
    b.total_tests = 11
    outcome, _ = compare_variants(a, b)
    assert outcome is ComparisonOutcome.INCOMPARABLE
