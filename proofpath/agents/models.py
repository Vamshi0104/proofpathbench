"""Provider-neutral model response records."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ModelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str
    requested_model: str
    resolved_model: str
    response_id: str | None = None
    output_text: str
    usage: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    elapsed_ms: int = Field(ge=0)
    empirical_eligible: bool


class PlanChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: Literal["A", "B"]
    rationale: str = Field(max_length=500)


class ManipulationChoice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stronger_evidence_candidate: Literal["A", "B", "equal", "incomparable"]
    higher_total_cost_candidate: Literal["A", "B", "equal"]
    rationale: str = Field(max_length=500)
