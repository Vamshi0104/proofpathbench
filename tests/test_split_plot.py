from collections import Counter

from proofpath.benchmark.design import split_plot_presentations, validate_split_plot, with_premium
from proofpath.benchmark.generate import generate_scenarios


def test_premium_clone_changes_only_cost_latency_and_design_cell() -> None:
    scenario = generate_scenarios()[0]
    clone = with_premium(scenario, 2.0)
    assert clone.scenario_id == scenario.scenario_id
    assert clone.goal == scenario.goal
    assert clone.initial_state == scenario.initial_state
    assert clone.failure_policy == scenario.failure_policy
    assert clone.verification_premium() == 2.0
    assert clone.plan(clone.evidence_dominant_plan_id()).total_latency_ms == 200


def test_split_plot_is_balanced_and_within_task() -> None:
    units = split_plot_presentations(generate_scenarios())
    assert validate_split_plot(units) == []
    per_task_premiums: dict[str, set[float]] = {}
    for scenario, _ in units:
        per_task_premiums.setdefault(scenario.scenario_id, set()).add(
            scenario.design_cell.verification_cost_multiplier
        )
    assert all(values == {1.0, 1.1, 1.5, 2.0} for values in per_task_premiums.values())
    assert Counter(variant for _, variant in units) == {
        "p1-o1": 96,
        "p1-o2": 96,
        "p2-o1": 96,
        "p2-o2": 96,
    }
