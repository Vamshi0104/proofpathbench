from proofpath.benchmark.generate import generate_scenarios
from proofpath.failures import derive_seed, sample_fault


def test_seed_derivation_is_stable_and_namespaced() -> None:
    first = derive_seed(20260928, "scenario-a", "run-1")
    assert first == derive_seed(20260928, "scenario-a", "run-1")
    assert first != derive_seed(20260928, "scenario-b", "run-1")
    assert first != derive_seed(20260928, "scenario-a", "run-2")


def test_sampled_fault_replays_exactly() -> None:
    scenario = next(
        item
        for item in generate_scenarios()
        if item.failure_policy.disclosed_probability == 0.2
    )
    assert sample_fault(scenario, 20260928, "replay") == sample_fault(
        scenario, 20260928, "replay"
    )


def test_zero_probability_never_activates() -> None:
    scenario = next(
        item
        for item in generate_scenarios()
        if item.failure_policy.disclosed_probability == 0.0
    )
    assert all(
        not sample_fault(scenario, 20260928, f"run-{index}").activated
        for index in range(100)
    )
