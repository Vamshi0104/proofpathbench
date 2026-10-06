"""Generate machine-readable diagnostics for known ProofPathBench choice confounds."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import correlation
from typing import Any

from proofpath.benchmark.generate import PROJECT_ROOT
from proofpath.benchmark.validate import load_scenarios


DEFAULT_OUTPUT = PROJECT_ROOT / "research" / "confound_diagnostics.json"


def build_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    mechanisms: Counter[str] = Counter()
    alias_sets: Counter[str] = Counter()
    dominant_positions: Counter[str] = Counter()
    prompt_templates: Counter[str] = Counter()
    for scenario in load_scenarios():
        dominant_id = scenario.evidence_dominant_plan_id()
        dominant = scenario.plan(dominant_id)
        baseline = next(plan for plan in scenario.candidate_plans if plan.plan_id != dominant_id)
        mechanisms[dominant.evidence_mechanism] += 1
        for variant in scenario.presentation_variants:
            alias_sets[variant.tool_alias_set] += 1
            prompt_templates[variant.prompt_template] += 1
            dominant_positions["1" if variant.plan_order[0] == dominant_id else "2"] += 1
        plan_rows = []
        for plan in scenario.candidate_plans:
            serialized = json.dumps(
                [step.model_dump(mode="json") for step in plan.steps],
                sort_keys=True,
                separators=(",", ":"),
            )
            plan_rows.append({
                "plan_id": plan.plan_id,
                "is_evidence_dominant": plan.plan_id == dominant_id,
                "operation_count": len(plan.steps),
                "distinct_tool_count": len({step.tool for step in plan.steps}),
                "serialized_step_characters": len(serialized),
                "verification_operations_after_mutation": max(0, len(plan.steps) - 1),
                "total_cost_units": plan.total_cost_units,
                "total_latency_ms": plan.total_latency_ms,
                "evidence_mechanism": plan.evidence_mechanism,
            })
        rows.append({
            "scenario_id": scenario.scenario_id,
            "domain": scenario.domain.value,
            "verification_premium": scenario.design_cell.verification_cost_multiplier,
            "risk": scenario.design_cell.disclosed_failure_probability,
            "severity": scenario.design_cell.severity,
            "plans": plan_rows,
            "dominant_minus_baseline": {
                "operation_count": len(dominant.steps) - len(baseline.steps),
                "distinct_tool_count": len({step.tool for step in dominant.steps}) - len({step.tool for step in baseline.steps}),
                "serialized_step_characters": len(json.dumps([step.model_dump(mode="json") for step in dominant.steps], sort_keys=True, separators=(",", ":"))) - len(json.dumps([step.model_dump(mode="json") for step in baseline.steps], sort_keys=True, separators=(",", ":"))),
                "total_cost_units": dominant.total_cost_units - baseline.total_cost_units,
                "total_latency_ms": dominant.total_latency_ms - baseline.total_latency_ms,
            },
        })

    flat = [plan for row in rows for plan in row["plans"]]
    costs = [float(plan["total_cost_units"]) for plan in flat]
    latency = [float(plan["total_latency_ms"]) for plan in flat]
    lengths = [float(plan["serialized_step_characters"]) for plan in flat]
    operations = [float(plan["operation_count"]) for plan in flat]
    return {
        "schema_version": "1.0",
        "status": "deterministic_design_diagnostic_not_behavioral_results",
        "scenario_count": len(rows),
        "plan_count": len(flat),
        "presentation_count": sum(alias_sets.values()),
        "balance": {
            "dominant_evidence_mechanism": dict(sorted(mechanisms.items())),
            "tool_alias_set": dict(sorted(alias_sets.items())),
            "prompt_template": dict(sorted(prompt_templates.items())),
            "dominant_plan_display_position": dict(sorted(dominant_positions.items())),
        },
        "correlations_across_plans": {
            "cost_latency_pearson": correlation(costs, latency),
            "operation_count_serialized_length_pearson": correlation(operations, lengths),
        },
        "known_couplings": [
            "The evidence-dominant plan necessarily contains one or more verification operations beyond the mutation and is therefore longer than the write-response-only baseline.",
            "Simulated cost and latency are varied jointly; their effects are not separately identifiable in version 1.",
            "Tool familiarity and perceived complexity may differ across verification mechanisms even though aliases, prompt templates, and display position are balanced.",
        ],
        "interpretation": "These diagnostics make residual design couplings explicit. They do not estimate behavioral confounding without model observations.",
        "scenarios": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build_report(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
