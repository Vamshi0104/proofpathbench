"""Outcome evaluation using authoritative state only."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from proofpath.benchmark.models import Scenario
from proofpath.environments.mock import MockEnvironment
from proofpath.environments.models import ExecutionTrace
from proofpath.environments.predicates import evaluate_predicate


class OutcomeEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str
    plan_id: str
    goal_satisfied: bool
    collateral_satisfied: bool
    verified_task_success: bool
    completion_claim: Literal["completed", "failed", "unresolved"]
    false_completion: bool
    duplicate_effect: bool


def evaluate_outcome(
    scenario: Scenario,
    environment: MockEnvironment,
    trace: ExecutionTrace,
    completion_claim: Literal["completed", "failed", "unresolved"],
) -> OutcomeEvaluation:
    state = environment.authoritative_state()
    goal = evaluate_predicate(state, scenario.postcondition)
    collateral = all(
        evaluate_predicate(state, predicate) for predicate in scenario.collateral_constraints
    )
    success = goal and collateral
    duplicate = any(event.event == "duplicate_commit" for event in environment.oracle_events())
    return OutcomeEvaluation(
        scenario_id=scenario.scenario_id,
        plan_id=trace.plan_id,
        goal_satisfied=goal,
        collateral_satisfied=collateral,
        verified_task_success=success,
        completion_claim=completion_claim,
        false_completion=completion_claim == "completed" and not success,
        duplicate_effect=duplicate,
    )
