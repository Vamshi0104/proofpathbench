from copy import deepcopy

import pytest

from proofpath.benchmark.generate import generate_scenarios
from proofpath.benchmark.design import split_plot_presentations
from proofpath.environments import MockEnvironment, execute_plan
from proofpath.evaluation import evaluate_outcome
from proofpath.failures import FailureType, forced_fault, no_fault


@pytest.fixture(scope="module")
def scenario():
    return generate_scenarios()[0]


def test_every_plan_is_semantically_equivalent_without_faults() -> None:
    for scenario, _ in split_plot_presentations(generate_scenarios()):
        for plan in scenario.candidate_plans:
            environment, trace = execute_plan(scenario, plan, no_fault())
            outcome = evaluate_outcome(scenario, environment, trace, "completed")
            assert outcome.verified_task_success, (scenario.scenario_id, plan.plan_id)
            assert not outcome.false_completion


@pytest.mark.parametrize(
    ("failure_type", "expected_success", "expected_goal", "expected_collateral"),
    [
        ("explicit_failure", False, False, False),
        ("false_success", False, False, False),
        ("timeout_before", False, False, False),
        ("timeout_after", True, True, True),
        ("partial_update", False, True, False),
        ("stale_readback", True, True, True),
        ("delayed_visibility", True, True, True),
        ("wrong_target", False, False, False),
        ("duplicated_action", True, True, True),
    ],
)
def test_each_forced_failure_has_expected_authoritative_outcome(
    scenario,
    failure_type: FailureType,
    expected_success: bool,
    expected_goal: bool,
    expected_collateral: bool,
) -> None:
    plan = scenario.plan(scenario.evidence_dominant_plan_id())
    environment, trace = execute_plan(scenario, plan, forced_fault(failure_type))
    outcome = evaluate_outcome(scenario, environment, trace, "completed")
    assert any(
        event.event == "fault_activated"
        and event.details["failure_type"] == failure_type
        for event in environment.oracle_events()
    )
    assert outcome.verified_task_success is expected_success
    assert outcome.goal_satisfied is expected_goal
    assert outcome.collateral_satisfied is expected_collateral
    assert outcome.false_completion is (not expected_success)
    assert outcome.duplicate_effect is (failure_type == "duplicated_action")


def test_false_success_response_is_not_ground_truth(scenario) -> None:
    weak_plan = next(
        plan for plan in scenario.candidate_plans if plan.evidence_mechanism == "write_response"
    )
    environment, trace = execute_plan(scenario, weak_plan, forced_fault("false_success"))
    assert trace.steps[0].result.status == "success"
    assert trace.steps[0].result.payload["reported_value"] == scenario.postcondition.expected
    outcome = evaluate_outcome(scenario, environment, trace, "completed")
    assert not outcome.verified_task_success
    assert outcome.false_completion


def test_tool_results_and_state_snapshots_are_isolated(scenario) -> None:
    environment = MockEnvironment(scenario, no_fault())
    mutation = environment.mutate(
        resource_id="file-001",
        field="content",
        value="approved-v2",
    )
    read = environment.readback("file-001")
    authoritative_before = environment.authoritative_state()
    visible_before = environment.visible_state()

    mutation.payload["reported_value"] = "tampered"
    read.payload["resource"]["content"] = "tampered"
    authoritative_before["resources"]["file-001"]["content"] = "tampered"
    visible_before["resources"]["file-001"]["content"] = "tampered"

    assert environment.authoritative_state()["resources"]["file-001"]["content"] == "approved-v2"
    assert environment.visible_state()["resources"]["file-001"]["content"] == "approved-v2"


def test_reset_by_reconstruction_is_deterministic(scenario) -> None:
    plan = scenario.plan("A")
    first_environment, first_trace = execute_plan(scenario, plan, no_fault(seed=7))
    second_environment, second_trace = execute_plan(scenario, plan, no_fault(seed=7))
    assert first_environment.authoritative_state() == second_environment.authoritative_state()
    assert first_environment.oracle_events() == second_environment.oracle_events()
    assert first_trace == second_trace
    assert first_environment.authoritative_state() != deepcopy(scenario.initial_state)
