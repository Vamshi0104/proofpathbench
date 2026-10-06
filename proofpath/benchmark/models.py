"""Typed, evaluator-side representation of ProofPathBench scenarios."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    """Base model that rejects undeclared manifest fields."""

    model_config = ConfigDict(extra="forbid")


class Domain(str, Enum):
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    PROFILE = "profile"
    CALENDAR = "calendar"
    MESSAGING = "messaging"
    CONFIGURATION = "configuration"
    COMMERCE = "commerce"
    SUBSCRIPTION = "subscription"


class EvidenceLevel(str, Enum):
    NONE = "none"
    WEAK = "weak"
    STRONG = "strong"


EVIDENCE_LEVEL_RANK = {
    EvidenceLevel.NONE: 0,
    EvidenceLevel.WEAK: 1,
    EvidenceLevel.STRONG: 2,
}


class Predicate(StrictModel):
    path: str = Field(min_length=1)
    operator: Literal["eq", "ne", "contains", "absent", "count_eq", "version_ge"]
    expected: Any = None


class EvidenceProfile(StrictModel):
    independence: EvidenceLevel
    authority: EvidenceLevel
    specificity: EvidenceLevel
    freshness: EvidenceLevel
    linkage: EvidenceLevel
    coverage: EvidenceLevel
    justification: str = Field(min_length=1)
    provenance_nodes: list[str] = Field(min_length=1)

    def vector(self) -> tuple[int, ...]:
        return tuple(
            EVIDENCE_LEVEL_RANK[value]
            for value in (
                self.independence,
                self.authority,
                self.specificity,
                self.freshness,
                self.linkage,
                self.coverage,
            )
        )

    def dominates(self, other: EvidenceProfile) -> bool:
        mine = self.vector()
        theirs = other.vector()
        return all(left >= right for left, right in zip(mine, theirs, strict=True)) and any(
            left > right for left, right in zip(mine, theirs, strict=True)
        )


class PlanStep(StrictModel):
    tool: Literal["mutate", "readback", "operation_status", "audit_read"]
    arguments: dict[str, Any]
    kind: Literal["mutation", "read", "status"]
    cost_units: float = Field(ge=0)
    latency_ms: int = Field(ge=0)


class CandidatePlan(StrictModel):
    plan_id: Literal["A", "B"]
    steps: list[PlanStep] = Field(min_length=1)
    total_cost_units: float = Field(gt=0)
    total_latency_ms: int = Field(ge=0)
    evidence_mechanism: Literal[
        "write_response", "independent_readback", "transaction_status", "multiple_source"
    ]
    evidence_profile: EvidenceProfile

    @model_validator(mode="after")
    def totals_match_steps(self) -> CandidatePlan:
        computed_cost = round(sum(step.cost_units for step in self.steps), 6)
        if abs(computed_cost - self.total_cost_units) > 1e-6:
            raise ValueError(
                f"declared cost {self.total_cost_units} does not match steps {computed_cost}"
            )
        computed_latency = sum(step.latency_ms for step in self.steps)
        if computed_latency != self.total_latency_ms:
            raise ValueError(
                f"declared latency {self.total_latency_ms} does not match steps {computed_latency}"
            )
        return self


class FailurePolicy(StrictModel):
    disclosed_probability: float = Field(json_schema_extra={"enum": [0.0, 0.05, 0.2]})
    allowed_failures: list[
        Literal[
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
    ]
    seed_namespace: str = Field(min_length=1)

    @field_validator("disclosed_probability")
    @classmethod
    def probability_is_supported(cls, value: float) -> float:
        if value not in {0.0, 0.05, 0.2}:
            raise ValueError("unsupported disclosed probability")
        return value


class Severity(StrictModel):
    level: Literal["low", "medium", "high"]
    state_consequence: dict[str, Any]
    penalty_units: float = Field(ge=0)


class ToolAliases(StrictModel):
    mutate: str = Field(min_length=1)
    readback: str = Field(min_length=1)
    operation_status: str = Field(min_length=1)
    audit_read: str = Field(min_length=1)


class PresentationVariant(StrictModel):
    variant_id: str = Field(pattern=r"^p[12]-o[12]$")
    prompt_template: Literal["task_direct_v1", "task_concise_v1"]
    tool_alias_set: Literal["neutral_alpha", "neutral_beta"]
    tool_aliases: ToolAliases
    plan_order: list[Literal["A", "B"]] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def plan_order_is_permutation(self) -> PresentationVariant:
        if set(self.plan_order) != {"A", "B"}:
            raise ValueError("plan_order must contain A and B exactly once")
        return self


class DesignCell(StrictModel):
    verification_cost_multiplier: float = Field(
        json_schema_extra={"enum": [1.0, 1.1, 1.5, 2.0]}
    )
    disclosed_failure_probability: float = Field(
        json_schema_extra={"enum": [0.0, 0.05, 0.2]}
    )
    severity: Literal["low", "high"]
    replicate: int = Field(ge=1, le=4)

    @field_validator("verification_cost_multiplier")
    @classmethod
    def premium_is_supported(cls, value: float) -> float:
        if value not in {1.0, 1.1, 1.5, 2.0}:
            raise ValueError("unsupported verification premium")
        return value

    @field_validator("disclosed_failure_probability")
    @classmethod
    def probability_is_supported(cls, value: float) -> float:
        if value not in {0.0, 0.05, 0.2}:
            raise ValueError("unsupported disclosed probability")
        return value


class Scenario(StrictModel):
    scenario_id: str = Field(pattern=r"^ppb-[a-z_]+-[0-9]{3}$")
    schema_version: Literal["0.2"] = "0.2"
    domain: Domain
    task_archetype: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    initial_state: dict[str, Any]
    postcondition: Predicate
    collateral_constraints: list[Predicate]
    candidate_plans: list[CandidatePlan] = Field(min_length=2, max_length=2)
    failure_policy: FailurePolicy
    severity: Severity
    design_cell: DesignCell
    presentation_variants: list[PresentationVariant] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def scenario_invariants(self) -> Scenario:
        if {plan.plan_id for plan in self.candidate_plans} != {"A", "B"}:
            raise ValueError("candidate plans must contain IDs A and B")
        if self.failure_policy.disclosed_probability != self.design_cell.disclosed_failure_probability:
            raise ValueError("failure probability disagrees with design cell")
        if self.severity.level != self.design_cell.severity:
            raise ValueError("severity disagrees with design cell")
        if {variant.variant_id for variant in self.presentation_variants} != {
            "p1-o1",
            "p1-o2",
            "p2-o1",
            "p2-o2",
        }:
            raise ValueError("four counterbalanced presentation variants are required")
        return self

    def plan(self, plan_id: str) -> CandidatePlan:
        return next(plan for plan in self.candidate_plans if plan.plan_id == plan_id)

    def evidence_dominant_plan_id(self) -> str:
        first, second = self.candidate_plans
        if first.evidence_profile.dominates(second.evidence_profile):
            return first.plan_id
        if second.evidence_profile.dominates(first.evidence_profile):
            return second.plan_id
        raise ValueError(f"{self.scenario_id} has no unique evidence-dominant plan")

    def verification_premium(self) -> float:
        dominant = self.plan(self.evidence_dominant_plan_id())
        other = next(plan for plan in self.candidate_plans if plan.plan_id != dominant.plan_id)
        return round(dominant.total_cost_units / other.total_cost_units, 2)
