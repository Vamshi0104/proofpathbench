from proofpath.benchmark.diagnostics import build_report


def test_confound_diagnostics_are_complete_and_balanced() -> None:
    report = build_report()
    assert report["scenario_count"] == 96
    assert report["plan_count"] == 192
    assert report["presentation_count"] == 384
    assert report["balance"]["dominant_evidence_mechanism"] == {
        "independent_readback": 32,
        "multiple_source": 32,
        "transaction_status": 32,
    }
    assert report["balance"]["dominant_plan_display_position"] == {"1": 192, "2": 192}
    assert report["correlations_across_plans"]["cost_latency_pearson"] == 1.0
    assert all(
        row["dominant_minus_baseline"]["operation_count"] >= 1
        and row["dominant_minus_baseline"]["serialized_step_characters"] > 0
        for row in report["scenarios"]
    )
