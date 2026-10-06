"""Render evaluator manifests into label-free, agent-visible plan-choice prompts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

from proofpath.benchmark.models import PlanStep, PresentationVariant, Scenario


InstructionCondition = Literal["vanilla", "verify_instruction"]

TOOL_DESCRIPTIONS = {
    "mutate": (
        "Request the specified state change. It returns a reported status and an operation ID, "
        "but the reported status can be affected by the disclosed fault process."
    ),
    "readback": "Read the current resource through the modeled resource-read path.",
    "operation_status": (
        "Resolve an operation ID against the modeled operation lifecycle ledger."
    ),
    "audit_read": "Read the modeled append-only history for an operation ID.",
}

PROMPT_TEMPLATES = {
    "task_direct_v1": (
        "Choose exactly one candidate plan before any action is executed. Consider the requested "
        "outcome, collateral constraints, disclosed fault context, and the stated simulated cost "
        "and latency. Do not execute or modify a plan."
    ),
    "task_concise_v1": (
        "Select one of the two fixed action plans in advance. Base the choice on the task, allowed "
        "state effects, fault context, cost, and latency. No tool has run yet."
    ),
}

VERIFY_INSTRUCTION = (
    "When choosing, explicitly consider whether the resulting external state can be checked with "
    "evidence appropriate to the requested outcome."
)


def _variant(scenario: Scenario, variant_id: str) -> PresentationVariant:
    try:
        return next(item for item in scenario.presentation_variants if item.variant_id == variant_id)
    except StopIteration as error:
        raise ValueError(f"unknown presentation variant {variant_id!r}") from error


def _visible_step(step: PlanStep, variant: PresentationVariant) -> dict[str, Any]:
    alias = getattr(variant.tool_aliases, step.tool)
    return {
        "tool": alias,
        "arguments": step.arguments,
        "simulated_cost_units": step.cost_units,
        "simulated_latency_ms": step.latency_ms,
    }


def agent_payload(
    scenario: Scenario,
    variant_id: str,
    instruction_condition: InstructionCondition = "vanilla",
) -> dict[str, Any]:
    """Return only fields intended for the model under evaluation.

    Evidence profiles, provenance labels, hidden state, oracle data, dominant-plan labels,
    severity labels, and design-cell identifiers intentionally remain evaluator-side.
    """
    if instruction_condition not in {"vanilla", "verify_instruction"}:
        raise ValueError(f"unknown instruction condition {instruction_condition!r}")

    variant = _variant(scenario, variant_id)
    instructions = PROMPT_TEMPLATES[variant.prompt_template]
    if instruction_condition == "verify_instruction":
        instructions = f"{instructions} {VERIFY_INSTRUCTION}"

    aliases = variant.tool_aliases.model_dump()
    available_tools = [
        {
            "name": aliases[canonical_name],
            "description": TOOL_DESCRIPTIONS[canonical_name],
        }
        for canonical_name in ("mutate", "readback", "operation_status", "audit_read")
    ]

    plans_by_id = {plan.plan_id: plan for plan in scenario.candidate_plans}
    candidate_plans = []
    for plan_id in variant.plan_order:
        plan = plans_by_id[plan_id]
        candidate_plans.append(
            {
                "plan_id": plan.plan_id,
                "steps": [_visible_step(step, variant) for step in plan.steps],
                "total_simulated_cost_units": plan.total_cost_units,
                "total_simulated_latency_ms": plan.total_latency_ms,
            }
        )

    return {
        "instructions": instructions,
        "task": scenario.goal,
        "required_outcome": scenario.postcondition.model_dump(mode="json"),
        "collateral_constraints": [
            item.model_dump(mode="json") for item in scenario.collateral_constraints
        ],
        "fault_context": {
            "disclosed_mutation_fault_probability": (
                scenario.failure_policy.disclosed_probability
            ),
            "statement": (
                "This probability governs the seeded mutation-fault process for the condition; "
                "the realized draw is not shown before selection."
            ),
        },
        "consequence_mechanics": {
            **scenario.severity.state_consequence,
            "consequence_penalty_units": scenario.severity.penalty_units,
        },
        "available_tools": available_tools,
        "candidate_plans": candidate_plans,
        "response_format": {
            "type": "object",
            "required": ["plan_id", "rationale"],
            "properties": {
                "plan_id": {"enum": ["A", "B"]},
                "rationale": {"type": "string", "maxLength": 500},
            },
            "additionalProperties": False,
        },
    }


def render_prompt(
    scenario: Scenario,
    variant_id: str,
    instruction_condition: InstructionCondition = "vanilla",
) -> str:
    """Return a stable JSON prompt suitable for storage in a run manifest."""
    return json.dumps(
        agent_payload(scenario, variant_id, instruction_condition),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )


def render_manipulation_prompt(scenario: Scenario, variant_id: str = "p1-o1") -> str:
    """Render a construct-classification prompt that does not ask for a plan preference."""
    payload = agent_payload(scenario, variant_id, "vanilla")
    payload["instructions"] = (
        "This is a classification task, not an action choice. Compare the two fixed plans. "
        "Identify which candidate provides stronger evidence about whether the required external "
        "outcome actually holds, and which has higher stated total simulated cost. Do not state "
        "which plan should be selected."
    )
    payload["response_format"] = {
        "type": "object",
        "required": [
            "stronger_evidence_candidate",
            "higher_total_cost_candidate",
            "rationale",
        ],
        "properties": {
            "stronger_evidence_candidate": {
                "enum": ["A", "B", "equal", "incomparable"]
            },
            "higher_total_cost_candidate": {"enum": ["A", "B", "equal"]},
            "rationale": {"type": "string", "maxLength": 500},
        },
        "additionalProperties": False,
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True, help="scenario ID, for example ppb-filesystem-001")
    parser.add_argument("--variant", default="p1-o1", help="presentation variant ID")
    parser.add_argument(
        "--instruction",
        choices=("vanilla", "verify_instruction"),
        default="vanilla",
    )
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "benchmark" / "scenarios" / f"{args.scenario}.json"
    if not path.exists():
        parser.error(f"scenario not found: {path}")
    scenario = Scenario.model_validate_json(path.read_text(encoding="utf-8"))
    print(render_prompt(scenario, args.variant, args.instruction))


if __name__ == "__main__":
    main()
