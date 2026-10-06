"""Prospective split-plot treatment expansion for the registered-choice pilot."""

from __future__ import annotations

from collections import Counter

from proofpath.benchmark.models import Scenario


PILOT_PREMIUMS = (1.0, 1.1, 1.5, 2.0)
PRESENTATION_IDS = ("p1-o1", "p1-o2", "p2-o1", "p2-o2")


def with_premium(scenario: Scenario, premium: float) -> Scenario:
    """Clone a base task and set only its evidence-step cost/latency premium."""
    if premium not in PILOT_PREMIUMS:
        raise ValueError(f"unsupported pilot premium {premium}")
    payload = scenario.model_dump(mode="python")
    dominant_id = scenario.evidence_dominant_plan_id()
    strong = next(plan for plan in payload["candidate_plans"] if plan["plan_id"] == dominant_id)
    evidence_steps = strong["steps"][1:]
    extra_cost = round(premium - 1.0, 6)
    extra_latency = round(100 * (premium - 1.0))
    first_cost = round(extra_cost / len(evidence_steps), 6)
    assigned_cost = 0.0
    assigned_latency = 0
    for index, step in enumerate(evidence_steps):
        if index == len(evidence_steps) - 1:
            step["cost_units"] = round(extra_cost - assigned_cost, 6)
            step["latency_ms"] = extra_latency - assigned_latency
        else:
            step["cost_units"] = first_cost
            step["latency_ms"] = extra_latency // len(evidence_steps)
            assigned_cost += first_cost
            assigned_latency += step["latency_ms"]
    strong["total_cost_units"] = premium
    strong["total_latency_ms"] = 100 + extra_latency
    payload["design_cell"]["verification_cost_multiplier"] = premium
    return Scenario.model_validate(payload)


def split_plot_presentations(
    scenarios: list[Scenario],
) -> list[tuple[Scenario, str]]:
    """Cross premium within task and rotate the four presentation variants."""
    units: list[tuple[Scenario, str]] = []
    for scenario_index, scenario in enumerate(sorted(scenarios, key=lambda item: item.scenario_id)):
        for premium_index, premium in enumerate(PILOT_PREMIUMS):
            variant_id = PRESENTATION_IDS[(scenario_index + premium_index) % len(PRESENTATION_IDS)]
            units.append((with_premium(scenario, premium), variant_id))
    return units


def validate_split_plot(units: list[tuple[Scenario, str]]) -> list[str]:
    errors: list[str] = []
    if len(units) != 384:
        errors.append(f"expected 384 split-plot units, found {len(units)}")
    by_task = Counter(scenario.scenario_id for scenario, _ in units)
    if set(by_task.values()) != {4}:
        errors.append("every base task must occur at all four premiums")
    cells = Counter(
        (
            scenario.design_cell.verification_cost_multiplier,
            scenario.design_cell.disclosed_failure_probability,
            scenario.design_cell.severity,
        )
        for scenario, _ in units
    )
    if len(cells) != 24 or set(cells.values()) != {16}:
        errors.append(f"expected 16 task instances in each of 24 cells, found {dict(cells)}")
    variants = Counter(variant for _, variant in units)
    if variants != {variant: 96 for variant in PRESENTATION_IDS}:
        errors.append(f"presentation variants not globally balanced: {dict(variants)}")
    for premium in PILOT_PREMIUMS:
        margin = Counter(
            variant
            for scenario, variant in units
            if scenario.design_cell.verification_cost_multiplier == premium
        )
        if margin != {variant: 24 for variant in PRESENTATION_IDS}:
            errors.append(f"premium {premium}: presentation imbalance: {dict(margin)}")
    for scenario, _ in units:
        if scenario.verification_premium() != scenario.design_cell.verification_cost_multiplier:
            errors.append(f"{scenario.scenario_id}: expanded premium mismatch")
    return errors
