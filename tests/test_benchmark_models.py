from proofpath.benchmark.generate import generate_scenarios


def test_generate_expected_scenario_count_and_domains() -> None:
    scenarios = generate_scenarios()
    assert len(scenarios) == 96
    assert len({scenario.domain for scenario in scenarios}) == 8
    assert all(
        sum(candidate.domain == scenario.domain for candidate in scenarios) == 12
        for scenario in scenarios
    )


def test_every_scenario_has_unique_evidence_dominance() -> None:
    scenarios = generate_scenarios()
    dominant_ids = [scenario.evidence_dominant_plan_id() for scenario in scenarios]
    assert dominant_ids.count("A") == 48
    assert dominant_ids.count("B") == 48


def test_matched_plans_only_add_observation_steps() -> None:
    for scenario in generate_scenarios():
        dominant = scenario.plan(scenario.evidence_dominant_plan_id())
        minimal = next(
            plan for plan in scenario.candidate_plans if plan.plan_id != dominant.plan_id
        )
        assert minimal.steps[0] == dominant.steps[0]
        assert [step.kind for step in dominant.steps[1:]]
        assert all(step.kind in {"read", "status"} for step in dominant.steps[1:])
        assert scenario.verification_premium() == scenario.design_cell.verification_cost_multiplier


def test_presentation_variants_counterbalance_order_and_aliases() -> None:
    for scenario in generate_scenarios():
        variants = scenario.presentation_variants
        assert sum(variant.plan_order == ["A", "B"] for variant in variants) == 2
        assert sum(variant.plan_order == ["B", "A"] for variant in variants) == 2
        assert {variant.tool_alias_set for variant in variants} == {
            "neutral_alpha",
            "neutral_beta",
        }
