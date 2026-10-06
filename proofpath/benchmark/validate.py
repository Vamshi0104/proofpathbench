"""Static Gate 2 validation for generated ProofPathBench manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from typing import Literal

from proofpath.benchmark.generate import INDEX_PATH, SCENARIO_DIR
from proofpath.benchmark.models import Domain, Scenario


PROHIBITED_AGENT_VISIBLE_TERMS = {
    "better_plan",
    "preferred_plan",
    "verified_plan",
    "evidence_dominant_plan",
    "recommended_plan",
}

REPORT_PATH = SCENARIO_DIR.parent / "validation_report.json"


def load_scenarios() -> list[Scenario]:
    paths = sorted(SCENARIO_DIR.glob("ppb-*.json"))
    return [Scenario.model_validate_json(path.read_text(encoding="utf-8")) for path in paths]


def validate_index(scenarios: list[Scenario]) -> list[str]:
    errors: list[str] = []
    if not INDEX_PATH.exists():
        return ["missing benchmark/scenarios/index.json"]
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if index.get("scenario_count") != len(scenarios):
        errors.append("index scenario_count does not match files")
    entries = index.get("scenarios", [])
    if len(entries) != len(scenarios):
        errors.append("index entry count does not match files")
    if len({entry.get("scenario_id") for entry in entries}) != len(entries):
        errors.append("index contains duplicate scenario IDs")
    by_id = {entry["scenario_id"]: entry for entry in entries}
    expected_ids = {scenario.scenario_id for scenario in scenarios}
    extra_ids = set(by_id) - expected_ids
    if extra_ids:
        errors.append(f"index contains unknown scenario IDs: {sorted(extra_ids)}")
    for scenario in scenarios:
        path = SCENARIO_DIR / f"{scenario.scenario_id}.json"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if scenario.scenario_id not in by_id:
            errors.append(f"{scenario.scenario_id}: absent from index")
        else:
            entry = by_id[scenario.scenario_id]
            if entry.get("path") != path.name:
                errors.append(f"{scenario.scenario_id}: index path mismatch")
            if entry.get("sha256") != digest:
                errors.append(f"{scenario.scenario_id}: index digest mismatch")
    return errors


def validate_scenarios(scenarios: list[Scenario]) -> list[str]:
    errors: list[str] = []
    if len(scenarios) != 96:
        errors.append(f"expected 96 scenarios, found {len(scenarios)}")
    if len({scenario.scenario_id for scenario in scenarios}) != len(scenarios):
        errors.append("scenario IDs are not unique")

    domain_counts = Counter(scenario.domain for scenario in scenarios)
    for domain in Domain:
        if domain_counts[domain] != 12:
            errors.append(f"{domain.value}: expected 12 scenarios, found {domain_counts[domain]}")

        domain_scenarios = [scenario for scenario in scenarios if scenario.domain == domain]
        premium_counts = Counter(
            scenario.design_cell.verification_cost_multiplier for scenario in domain_scenarios
        )
        if premium_counts != {1.0: 3, 1.1: 3, 1.5: 3, 2.0: 3}:
            errors.append(f"{domain.value}: premium levels not balanced: {dict(premium_counts)}")
        risk_counts = Counter(
            scenario.design_cell.disclosed_failure_probability for scenario in domain_scenarios
        )
        if risk_counts != {0.0: 4, 0.05: 4, 0.2: 4}:
            errors.append(f"{domain.value}: risk levels not balanced: {dict(risk_counts)}")
        severity_counts = Counter(scenario.design_cell.severity for scenario in domain_scenarios)
        if severity_counts != {"low": 6, "high": 6}:
            errors.append(f"{domain.value}: severity levels not balanced: {dict(severity_counts)}")
        domain_dominant_counts = Counter(
            scenario.evidence_dominant_plan_id() for scenario in domain_scenarios
        )
        if domain_dominant_counts != {"A": 6, "B": 6}:
            errors.append(
                f"{domain.value}: dominant-plan labels not balanced: {dict(domain_dominant_counts)}"
            )
        domain_mechanism_counts = Counter(
            scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism
            for scenario in domain_scenarios
        )
        if set(domain_mechanism_counts) != {
            "independent_readback",
            "transaction_status",
            "multiple_source",
        } or not all(2 <= count <= 6 for count in domain_mechanism_counts.values()):
            errors.append(
                f"{domain.value}: evidence mechanisms lack within-domain coverage: "
                f"{dict(domain_mechanism_counts)}"
            )

    cells = Counter(
        (
            scenario.design_cell.verification_cost_multiplier,
            scenario.design_cell.disclosed_failure_probability,
            scenario.design_cell.severity,
        )
        for scenario in scenarios
    )
    if len(cells) != 24:
        errors.append(f"expected 24 treatment cells, found {len(cells)}")
    for cell, count in sorted(cells.items()):
        if count != 4:
            errors.append(f"cell {cell}: expected 4 scenarios, found {count}")

        cell_scenarios = [
            scenario
            for scenario in scenarios
            if (
                scenario.design_cell.verification_cost_multiplier,
                scenario.design_cell.disclosed_failure_probability,
                scenario.design_cell.severity,
            )
            == cell
        ]
        cell_labels = Counter(
            scenario.evidence_dominant_plan_id() for scenario in cell_scenarios
        )
        if cell_labels != {"A": 2, "B": 2}:
            errors.append(f"cell {cell}: dominant-plan labels not balanced: {dict(cell_labels)}")
        cell_mechanisms = Counter(
            scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism
            for scenario in cell_scenarios
        )
        if sorted(cell_mechanisms.values()) != [1, 1, 2]:
            errors.append(
                f"cell {cell}: expected a counterbalanced 2/1/1 mechanism split, "
                f"found {dict(cell_mechanisms)}"
            )

    replicate_counts = Counter(
        (
            scenario.design_cell.verification_cost_multiplier,
            scenario.design_cell.disclosed_failure_probability,
            scenario.design_cell.severity,
            scenario.design_cell.replicate,
        )
        for scenario in scenarios
    )
    if len(replicate_counts) != 96 or any(count != 1 for count in replicate_counts.values()):
        errors.append("treatment-cell replicate identifiers are not unique")

    dominant_counts = Counter(scenario.evidence_dominant_plan_id() for scenario in scenarios)
    if dominant_counts != {"A": 48, "B": 48}:
        errors.append(f"dominant-plan labels not balanced: {dict(dominant_counts)}")

    mechanism_counts = Counter(
        scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism
        for scenario in scenarios
    )
    if mechanism_counts != {
        "independent_readback": 32,
        "transaction_status": 32,
        "multiple_source": 32,
    }:
        errors.append(f"evidence mechanisms not balanced: {dict(mechanism_counts)}")

    mechanism_names: tuple[
        Literal["independent_readback", "transaction_status", "multiple_source"], ...
    ] = (
        "independent_readback",
        "transaction_status",
        "multiple_source",
    )
    for premium in (1.0, 1.1, 1.5, 2.0):
        counts = Counter(
            scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism
            for scenario in scenarios
            if scenario.design_cell.verification_cost_multiplier == premium
        )
        if counts != {name: 8 for name in mechanism_names}:
            errors.append(f"premium {premium}: mechanism imbalance: {dict(counts)}")
    for risk in (0.0, 0.05, 0.2):
        counts = Counter(
            scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism
            for scenario in scenarios
            if scenario.design_cell.disclosed_failure_probability == risk
        )
        margin = [counts.get(name, 0) for name in mechanism_names]
        if set(margin) != {10, 11} or max(margin) - min(margin) != 1:
            errors.append(f"risk {risk}: mechanism imbalance: {dict(counts)}")
    for severity in ("low", "high"):
        counts = Counter(
            scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism
            for scenario in scenarios
            if scenario.design_cell.severity == severity
        )
        if counts != {name: 16 for name in mechanism_names}:
            errors.append(f"severity {severity}: mechanism imbalance: {dict(counts)}")

    for scenario in scenarios:
        dominant_id = scenario.evidence_dominant_plan_id()
        dominant = scenario.plan(dominant_id)
        minimal = next(plan for plan in scenario.candidate_plans if plan.plan_id != dominant_id)
        if scenario.verification_premium() != scenario.design_cell.verification_cost_multiplier:
            errors.append(f"{scenario.scenario_id}: verification premium mismatch")
        expected_latency = round(100 * scenario.design_cell.verification_cost_multiplier)
        if dominant.total_latency_ms != expected_latency:
            errors.append(
                f"{scenario.scenario_id}: verification latency premium mismatch "
                f"({dominant.total_latency_ms} != {expected_latency})"
            )
        if minimal.steps[0] != dominant.steps[0]:
            errors.append(f"{scenario.scenario_id}: mutation steps are not matched")
        if any(step.kind == "mutation" for step in dominant.steps[1:]):
            errors.append(f"{scenario.scenario_id}: evidence plan adds a mutation")
        if len(minimal.steps) != 1 or minimal.steps[0].kind != "mutation":
            errors.append(f"{scenario.scenario_id}: minimal plan is not mutation-only")

        visible_material = " ".join(
            [scenario.goal, scenario.task_archetype]
            + [alias for variant in scenario.presentation_variants for alias in variant.tool_aliases.model_dump().values()]
        ).lower()
        for term in PROHIBITED_AGENT_VISIBLE_TERMS:
            if term in visible_material:
                errors.append(f"{scenario.scenario_id}: prohibited label {term!r} leaked")
    return errors


def validation_report(scenarios: list[Scenario]) -> dict[str, object]:
    errors = validate_index(scenarios) + validate_scenarios(scenarios)
    return {
        "valid": not errors,
        "scenario_count": len(scenarios),
        "domain_counts": dict(sorted(Counter(item.domain.value for item in scenarios).items())),
        "treatment_cell_count": len(
            {
                (
                    item.design_cell.verification_cost_multiplier,
                    item.design_cell.disclosed_failure_probability,
                    item.design_cell.severity,
                )
                for item in scenarios
            }
        ),
        "evidence_mechanism_counts": dict(
            sorted(
                Counter(
                    item.plan(item.evidence_dominant_plan_id()).evidence_mechanism
                    for item in scenarios
                ).items()
            )
        ),
        "dominant_plan_counts": dict(
            sorted(Counter(item.evidence_dominant_plan_id() for item in scenarios).items())
        ),
        "mechanism_balance_by_factor": {
            "premium": {
                str(premium): dict(
                    sorted(
                        Counter(
                            item.plan(item.evidence_dominant_plan_id()).evidence_mechanism
                            for item in scenarios
                            if item.design_cell.verification_cost_multiplier == premium
                        ).items()
                    )
                )
                for premium in (1.0, 1.1, 1.5, 2.0)
            },
            "risk": {
                str(risk): dict(
                    sorted(
                        Counter(
                            item.plan(item.evidence_dominant_plan_id()).evidence_mechanism
                            for item in scenarios
                            if item.design_cell.disclosed_failure_probability == risk
                        ).items()
                    )
                )
                for risk in (0.0, 0.05, 0.2)
            },
            "severity": {
                severity: dict(
                    sorted(
                        Counter(
                            item.plan(item.evidence_dominant_plan_id()).evidence_mechanism
                            for item in scenarios
                            if item.design_cell.severity == severity
                        ).items()
                    )
                )
                for severity in ("low", "high")
            },
        },
        "within_domain_balance": {
            domain.value: {
                "premiums": dict(
                    sorted(
                        Counter(
                            str(item.design_cell.verification_cost_multiplier)
                            for item in scenarios
                            if item.domain == domain
                        ).items()
                    )
                ),
                "risks": dict(
                    sorted(
                        Counter(
                            str(item.design_cell.disclosed_failure_probability)
                            for item in scenarios
                            if item.domain == domain
                        ).items()
                    )
                ),
                "severities": dict(
                    sorted(
                        Counter(
                            item.design_cell.severity
                            for item in scenarios
                            if item.domain == domain
                        ).items()
                    )
                ),
            }
            for domain in Domain
        },
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-report",
        action="store_true",
        help=f"write the canonical report to {REPORT_PATH}",
    )
    args = parser.parse_args()
    scenarios = load_scenarios()
    report = validation_report(scenarios)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_report:
        REPORT_PATH.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
