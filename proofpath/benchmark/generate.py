"""Deterministically generate the 96 ProofPathBench Gate 2 manifests."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any, Literal, cast

from proofpath.benchmark.catalog import CATALOG, TaskTemplate, validate_catalog
from proofpath.benchmark.models import (
    CandidatePlan,
    DesignCell,
    Domain,
    EvidenceLevel,
    EvidenceProfile,
    FailurePolicy,
    PlanStep,
    Predicate,
    PresentationVariant,
    Scenario,
    Severity,
    ToolAliases,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = PROJECT_ROOT / "benchmark" / "scenarios"
SCHEMA_PATH = PROJECT_ROOT / "benchmark" / "schemas" / "scenario.schema.json"
INDEX_PATH = SCENARIO_DIR / "index.json"

FAILURE_TYPES = [
    "explicit_failure",
    "false_success",
    "timeout_before",
    "timeout_after",
    "partial_update",
    "stale_readback",
    "delayed_visibility",
    "wrong_target",
    "duplicated_action",
]

ALPHA_ALIASES = ToolAliases(
    mutate="apply_change",
    readback="inspect_resource",
    operation_status="lookup_operation",
    audit_read="inspect_history",
)
BETA_ALIASES = ToolAliases(
    mutate="commit_update",
    readback="fetch_resource",
    operation_status="get_operation",
    audit_read="fetch_history",
)

WEAK_PROFILE = EvidenceProfile(
    independence=EvidenceLevel.NONE,
    authority=EvidenceLevel.WEAK,
    specificity=EvidenceLevel.WEAK,
    freshness=EvidenceLevel.WEAK,
    linkage=EvidenceLevel.WEAK,
    coverage=EvidenceLevel.WEAK,
    justification=(
        "The only evidence is the mutation response, which shares the mutation failure boundary "
        "and does not independently establish authoritative state."
    ),
    provenance_nodes=["mutation_service", "mutation_response"],
)

STRONG_PROFILES: dict[str, EvidenceProfile] = {
    "independent_readback": EvidenceProfile(
        independence=EvidenceLevel.STRONG,
        authority=EvidenceLevel.STRONG,
        specificity=EvidenceLevel.STRONG,
        freshness=EvidenceLevel.STRONG,
        linkage=EvidenceLevel.STRONG,
        coverage=EvidenceLevel.STRONG,
        justification=(
            "A separately modeled authoritative read path observes the target field, entity ID, "
            "version, and collateral-state summary after the mutation."
        ),
        provenance_nodes=["mutation_service", "authoritative_store", "read_service"],
    ),
    "transaction_status": EvidenceProfile(
        independence=EvidenceLevel.STRONG,
        authority=EvidenceLevel.STRONG,
        specificity=EvidenceLevel.STRONG,
        freshness=EvidenceLevel.STRONG,
        linkage=EvidenceLevel.STRONG,
        coverage=EvidenceLevel.STRONG,
        justification=(
            "An immutable operation ID is resolved against an authoritative lifecycle ledger that "
            "records the target, committed value, version, and collateral-state summary."
        ),
        provenance_nodes=["mutation_service", "operation_ledger", "status_service"],
    ),
    "multiple_source": EvidenceProfile(
        independence=EvidenceLevel.STRONG,
        authority=EvidenceLevel.STRONG,
        specificity=EvidenceLevel.STRONG,
        freshness=EvidenceLevel.STRONG,
        linkage=EvidenceLevel.STRONG,
        coverage=EvidenceLevel.STRONG,
        justification=(
            "Authoritative readback and an append-only audit projection independently identify the "
            "entity, intended value, committed version, and collateral-state summary."
        ),
        provenance_nodes=[
            "mutation_service",
            "authoritative_store",
            "read_service",
            "audit_projection",
        ],
    ),
}


def design_cells() -> list[DesignCell]:
    """Return a domain-balanced assignment with four replications per 24-cell treatment.

    A parity construction assigns each treatment cell to four of eight domains. Within
    every domain, premium is balanced 3/level, risk 4/level, and severity 6/level.
    """
    cells: list[DesignCell] = []
    for premium, risk, severity_value in product(
        (1.0, 1.1, 1.5, 2.0), (0.0, 0.05, 0.2), ("low", "high")
    ):
        severity = cast(Literal["low", "high"], severity_value)
        for replicate in range(1, 5):
            cells.append(
                DesignCell(
                    verification_cost_multiplier=premium,
                    disclosed_failure_probability=risk,
                    severity=severity,
                    replicate=replicate,
                )
            )
    return cells


def _presentation_variants() -> list[PresentationVariant]:
    return [
        PresentationVariant(
            variant_id="p1-o1",
            prompt_template="task_direct_v1",
            tool_alias_set="neutral_alpha",
            tool_aliases=ALPHA_ALIASES,
            plan_order=["A", "B"],
        ),
        PresentationVariant(
            variant_id="p1-o2",
            prompt_template="task_direct_v1",
            tool_alias_set="neutral_beta",
            tool_aliases=BETA_ALIASES,
            plan_order=["B", "A"],
        ),
        PresentationVariant(
            variant_id="p2-o1",
            prompt_template="task_concise_v1",
            tool_alias_set="neutral_beta",
            tool_aliases=BETA_ALIASES,
            plan_order=["A", "B"],
        ),
        PresentationVariant(
            variant_id="p2-o2",
            prompt_template="task_concise_v1",
            tool_alias_set="neutral_alpha",
            tool_aliases=ALPHA_ALIASES,
            plan_order=["B", "A"],
        ),
    ]


def _strong_steps(
    mechanism: str,
    resource_id: str,
    premium: float,
) -> list[PlanStep]:
    extra_cost = round(premium - 1.0, 6)
    extra_latency = round(100 * (premium - 1.0))
    if mechanism == "independent_readback":
        return [
            PlanStep(
                tool="readback",
                arguments={"resource_id": resource_id, "freshness": "current"},
                kind="read",
                cost_units=extra_cost,
                latency_ms=extra_latency,
            )
        ]
    if mechanism == "transaction_status":
        return [
            PlanStep(
                tool="operation_status",
                arguments={"operation_id": "$mutation.operation_id"},
                kind="status",
                cost_units=extra_cost,
                latency_ms=extra_latency,
            )
        ]
    first_cost = round(extra_cost / 2, 6)
    first_latency = extra_latency // 2
    return [
        PlanStep(
            tool="readback",
            arguments={"resource_id": resource_id, "freshness": "current"},
            kind="read",
            cost_units=first_cost,
            latency_ms=first_latency,
        ),
        PlanStep(
            tool="audit_read",
            arguments={"operation_id": "$mutation.operation_id"},
            kind="read",
            cost_units=round(extra_cost - first_cost, 6),
            latency_ms=extra_latency - first_latency,
        ),
    ]


def _plans(
    template: TaskTemplate,
    resource_id: str,
    cell: DesignCell,
    mechanism_index: int,
    dominant_plan_id: str,
) -> list[CandidatePlan]:
    mutation = PlanStep(
        tool="mutate",
        arguments={
            "resource_id": resource_id,
            "field": template.field,
            "value": template.target,
        },
        kind="mutation",
        cost_units=1.0,
        latency_ms=100,
    )
    mechanism = ("independent_readback", "transaction_status", "multiple_source")[
        mechanism_index
    ]
    strong_steps = [mutation.model_copy(deep=True)] + _strong_steps(
        mechanism,
        resource_id,
        cell.verification_cost_multiplier,
    )
    weak_plan = CandidatePlan(
        plan_id="B" if dominant_plan_id == "A" else "A",
        steps=[mutation.model_copy(deep=True)],
        total_cost_units=1.0,
        total_latency_ms=100,
        evidence_mechanism="write_response",
        evidence_profile=WEAK_PROFILE,
    )
    strong_plan = CandidatePlan(
        plan_id=dominant_plan_id,  # type: ignore[arg-type]
        steps=strong_steps,
        total_cost_units=cell.verification_cost_multiplier,
        total_latency_ms=sum(step.latency_ms for step in strong_steps),
        evidence_mechanism=mechanism,  # type: ignore[arg-type]
        evidence_profile=STRONG_PROFILES[mechanism],
    )
    return [weak_plan, strong_plan]


def _scenario(
    domain: Domain,
    local_index: int,
    template: TaskTemplate,
    cell: DesignCell,
    mechanism_index: int,
    dominant_plan_id: str,
) -> Scenario:
    resource_id = f"{template.noun}-{local_index:03d}"
    scenario_id = f"ppb-{domain.value}-{local_index:03d}"
    severity_count = 1 if cell.severity == "low" else 20
    consequence = {
        "affected_mock_dependents": severity_count,
        "recovery_actions_required": 1 if cell.severity == "low" else 5,
        "description": (
            "One isolated mock dependent consumes the resulting state."
            if cell.severity == "low"
            else "Twenty mock dependents consume the resulting state before the next checkpoint."
        ),
    }
    return Scenario(
        scenario_id=scenario_id,
        domain=domain,
        task_archetype=template.archetype,
        goal=(
            f"{template.verb.capitalize()} the mock {template.noun} {resource_id} so that "
            f"{template.field} is {template.target!r}."
        ),
        initial_state={
            "resources": {
                resource_id: {
                    "kind": template.noun,
                    template.field: template.initial,
                    "version": 1,
                    "last_operation_id": None,
                }
            },
            "operation_ledger": {},
            "audit_projection": [],
            "mock_dependents": severity_count,
        },
        postcondition=Predicate(
            path=f"resources.{resource_id}.{template.field}",
            operator="eq",
            expected=template.target,
        ),
        collateral_constraints=[
            Predicate(path="resources.__count__", operator="count_eq", expected=1),
            Predicate(path=f"resources.{resource_id}.version", operator="version_ge", expected=2),
        ],
        candidate_plans=_plans(
            template,
            resource_id,
            cell,
            mechanism_index,
            dominant_plan_id,
        ),
        failure_policy=FailurePolicy(
            disclosed_probability=cell.disclosed_failure_probability,
            allowed_failures=FAILURE_TYPES,  # type: ignore[arg-type]
            seed_namespace=f"proofpathbench:{scenario_id}",
        ),
        severity=Severity(
            level=cell.severity,
            state_consequence=consequence,
            penalty_units=1.0 if cell.severity == "low" else 10.0,
        ),
        design_cell=cell,
        presentation_variants=_presentation_variants(),
    )


def generate_scenarios() -> list[Scenario]:
    validate_catalog()
    scenarios: list[Scenario] = []
    domains = list(Domain)
    premiums = (1.0, 1.1, 1.5, 2.0)
    risks = (0.0, 0.05, 0.2)
    severities: tuple[Literal["low", "high"], ...] = ("low", "high")
    replicate_by_cell: dict[tuple[float, float, str], int] = Counter()
    for domain_index, domain in enumerate(domains):
        assigned: list[tuple[DesignCell, int, str]] = []
        for premium_index, premium in enumerate(premiums):
            for risk_index, risk in enumerate(risks):
                for severity_index, severity in enumerate(severities):
                    if (domain_index + premium_index + risk_index + severity_index) % 2:
                        continue
                    key = (premium, risk, severity)
                    replicate_by_cell[key] += 1
                    cell = DesignCell(
                        verification_cost_multiplier=premium,
                        disclosed_failure_probability=risk,
                        severity=severity,
                        replicate=replicate_by_cell[key],
                    )
                    # The nuisance mechanism is balanced globally and across every primary
                    # factor margin. Four replications cannot be divided equally over three
                    # mechanisms, so each treatment cell has a preregistered 2/1/1 split.
                    mechanism_index = (
                        cell.replicate
                        - 1
                        + premium_index
                        + risk_index
                        + severity_index
                    ) % 3
                    # Strong-plan labels are 2/2 in every treatment cell and 6/6 per domain.
                    dominant_plan_id = (
                        "A" if (domain_index // 2 + premium_index) % 2 == 0 else "B"
                    )
                    assigned.append((cell, mechanism_index, dominant_plan_id))
        if len(assigned) != 12:
            raise AssertionError(f"{domain.value} received {len(assigned)} cells")
        for local_index, (cell, mechanism_index, dominant_plan_id) in enumerate(
            assigned, start=1
        ):
            template = CATALOG[domain][local_index - 1]
            scenarios.append(
                _scenario(
                    domain,
                    local_index,
                    template,
                    cell,
                    mechanism_index,
                    dominant_plan_id,
                )
            )
    return scenarios


def _canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def write_artifacts(scenarios: list[Scenario]) -> None:
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)

    expected_files: set[Path] = set()
    index_entries: list[dict[str, Any]] = []
    for scenario in scenarios:
        path = SCENARIO_DIR / f"{scenario.scenario_id}.json"
        expected_files.add(path)
        payload = _canonical_json(scenario.model_dump(mode="json"))
        path.write_text(payload, encoding="utf-8")
        index_entries.append(
            {
                "scenario_id": scenario.scenario_id,
                "path": path.name,
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            }
        )

    for old_path in SCENARIO_DIR.glob("ppb-*.json"):
        if old_path not in expected_files:
            old_path.unlink()

    index_payload = {
        "schema_version": "0.2",
        "generator": "proofpath.benchmark.generate",
        "scenario_count": len(scenarios),
        "scenarios": index_entries,
    }
    INDEX_PATH.write_text(_canonical_json(index_payload), encoding="utf-8")
    SCHEMA_PATH.write_text(
        _canonical_json(Scenario.model_json_schema()),
        encoding="utf-8",
    )


def main() -> None:
    scenarios = generate_scenarios()
    write_artifacts(scenarios)
    print(f"generated {len(scenarios)} scenarios in {SCENARIO_DIR}")


if __name__ == "__main__":
    main()
