import json

import pytest

from proofpath.benchmark.generate import generate_scenarios
from proofpath.benchmark.render import agent_payload, render_prompt

HIDDEN_TERMS = {
    "evidence_profile",
    "evidence_mechanism",
    "evidence_dominant_plan",
    "dominant_plan_id",
    "provenance_nodes",
    "design_cell",
    "initial_state",
    "seed_namespace",
    "severity",
}


@pytest.fixture(scope="module")
def scenario():
    return generate_scenarios()[0]


def test_agent_payload_does_not_leak_evaluator_fields(scenario) -> None:
    for variant in scenario.presentation_variants:
        for condition in ("vanilla", "verify_instruction"):
            serialized = json.dumps(agent_payload(scenario, variant.variant_id, condition)).lower()
            for term in HIDDEN_TERMS:
                assert term not in serialized
            assert scenario.failure_policy.seed_namespace not in serialized


def test_plan_order_and_aliases_follow_variant(scenario) -> None:
    for variant in scenario.presentation_variants:
        payload = agent_payload(scenario, variant.variant_id)
        assert [plan["plan_id"] for plan in payload["candidate_plans"]] == variant.plan_order
        visible_tools = {item["name"] for item in payload["available_tools"]}
        assert visible_tools == set(variant.tool_aliases.model_dump().values())
        canonical_tools = {"mutate", "readback", "operation_status", "audit_read"}
        assert not (visible_tools & canonical_tools)


def test_instruction_manipulation_changes_only_instructions(scenario) -> None:
    vanilla = agent_payload(scenario, "p1-o1", "vanilla")
    instructed = agent_payload(scenario, "p1-o1", "verify_instruction")
    assert vanilla["instructions"] != instructed["instructions"]
    vanilla["instructions"] = ""
    instructed["instructions"] = ""
    assert vanilla == instructed


def test_prompt_is_stable_json(scenario) -> None:
    first = render_prompt(scenario, "p2-o2")
    assert first == render_prompt(scenario, "p2-o2")
    assert json.loads(first)["response_format"]["properties"]["plan_id"]["enum"] == ["A", "B"]


def test_unknown_variant_and_condition_fail(scenario) -> None:
    with pytest.raises(ValueError):
        agent_payload(scenario, "unknown")
    with pytest.raises(ValueError):
        agent_payload(scenario, "p1-o1", "unknown")  # type: ignore[arg-type]
