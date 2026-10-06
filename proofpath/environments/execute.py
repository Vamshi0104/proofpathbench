"""Candidate-plan execution against the deterministic mock environment."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from proofpath.benchmark.models import CandidatePlan, Scenario
from proofpath.environments.mock import MockEnvironment
from proofpath.environments.models import ExecutionTrace, ToolResult, TraceStep
from proofpath.failures.models import FaultSpec


def _resolve(value: Any, prior_results: list[ToolResult]) -> Any:
    if value == "$mutation.operation_id":
        for result in prior_results:
            if result.tool == "mutate":
                return result.payload.get("operation_id")
        return None
    if isinstance(value, dict):
        return {key: _resolve(item, prior_results) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve(item, prior_results) for item in value]
    return deepcopy(value)


def execute_plan(
    scenario: Scenario,
    plan: CandidatePlan,
    fault: FaultSpec,
) -> tuple[MockEnvironment, ExecutionTrace]:
    environment = MockEnvironment(scenario, fault)
    results: list[ToolResult] = []
    trace_steps: list[TraceStep] = []
    for index, step in enumerate(plan.steps, start=1):
        arguments = _resolve(step.arguments, results)
        tool = getattr(environment, step.tool)
        result: ToolResult = tool(**arguments)
        results.append(result)
        trace_steps.append(
            TraceStep(index=index, tool=step.tool, arguments=arguments, result=result)
        )
    trace = ExecutionTrace(
        scenario_id=scenario.scenario_id,
        plan_id=plan.plan_id,
        fault_activated=fault.activated,
        failure_type=fault.failure_type,
        derived_seed=fault.derived_seed,
        steps=trace_steps,
    )
    return environment, trace
