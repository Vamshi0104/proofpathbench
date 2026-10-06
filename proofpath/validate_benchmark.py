"""Run static and deterministic runtime acceptance checks for ProofPathBench."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from proofpath.benchmark.generate import INDEX_PATH
from proofpath.benchmark.design import split_plot_presentations, validate_split_plot
from proofpath.benchmark.validate import load_scenarios, validate_index, validate_scenarios
from proofpath.environments import MockEnvironment, execute_plan
from proofpath.evaluation import evaluate_outcome
from proofpath.failures import FailureType, forced_fault, no_fault


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "pilot.yaml"
DEFAULT_REPORT = PROJECT_ROOT / "benchmark" / "runtime_validation_report.json"
FAILURES: tuple[FailureType, ...] = (
    "explicit_failure",
    "false_success",
    "timeout_before",
    "timeout_after",
    "partial_update",
    "stale_readback",
    "delayed_visibility",
    "wrong_target",
    "duplicated_action",
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_validation(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    scenarios = load_scenarios()
    errors = validate_index(scenarios) + validate_scenarios(scenarios)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if config["study"]["base_scenarios"] != len(scenarios):
        errors.append("config base_scenarios does not match generated scenario count")

    units = split_plot_presentations(scenarios)
    split_errors = validate_split_plot(units)
    errors.extend(split_errors)
    no_fault_executions = 0
    for scenario, _ in units:
        for plan in scenario.candidate_plans:
            environment, trace = execute_plan(scenario, plan, no_fault())
            outcome = evaluate_outcome(scenario, environment, trace, "completed")
            no_fault_executions += 1
            if not outcome.verified_task_success:
                errors.append(
                    f"{scenario.scenario_id}/{plan.plan_id}: no-fault semantic equivalence failed"
                )

    representative = scenarios[0]
    representative_plan = representative.plan(representative.evidence_dominant_plan_id())
    failure_results: dict[str, Any] = {}
    for failure_type in FAILURES:
        environment, trace = execute_plan(
            representative,
            representative_plan,
            forced_fault(failure_type),
        )
        outcome = evaluate_outcome(representative, environment, trace, "completed")
        activated = any(
            event.event == "fault_activated"
            and event.details.get("failure_type") == failure_type
            for event in environment.oracle_events()
        )
        if not activated:
            errors.append(f"{failure_type}: forced fault did not activate")
        failure_results[failure_type] = {
            "activated": activated,
            "goal_satisfied": outcome.goal_satisfied,
            "collateral_satisfied": outcome.collateral_satisfied,
            "verified_task_success": outcome.verified_task_success,
            "false_completion_if_claimed": outcome.false_completion,
            "duplicate_effect": outcome.duplicate_effect,
        }

    isolation_environment = MockEnvironment(representative, no_fault())
    mutation_arguments = representative_plan.steps[0].arguments
    resource_id = mutation_arguments["resource_id"]
    field = mutation_arguments["field"]
    target_value = mutation_arguments["value"]
    isolation_environment.mutate(resource_id, field, target_value)
    response = isolation_environment.readback(resource_id)
    response.payload["resource"][field] = "tampered"
    snapshot = isolation_environment.authoritative_state()
    snapshot["resources"][resource_id][field] = "also-tampered"
    isolation_passed = (
        isolation_environment.authoritative_state()["resources"][resource_id][field]
        == target_value
    )
    if not isolation_passed:
        errors.append("tool/evaluator state isolation failed")

    return {
        "valid": not errors,
        "scope": "deterministic pre-pilot runtime acceptance; not an empirical result",
        "config_path": str(config_path.relative_to(PROJECT_ROOT)),
        "config_sha256": _digest(config_path),
        "scenario_index_sha256": _digest(INDEX_PATH),
        "scenario_count": len(scenarios),
        "no_fault_plan_executions": no_fault_executions,
        "split_plot_unit_count": len(units),
        "split_plot_valid": not split_errors,
        "no_fault_semantic_equivalence_passed": no_fault_executions == 768 and not any(
            "semantic equivalence failed" in error for error in errors
        ),
        "state_isolation_passed": isolation_passed,
        "forced_failure_results": failure_results,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report = runtime_validation(args.config.resolve())
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_report:
        args.report.resolve().write_text(payload, encoding="utf-8")
    print(payload, end="")
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
