"""Execution records shared by the environment, runner, and evaluator."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FrozenRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ToolResult(FrozenRecord):
    tool: str
    status: Literal["success", "error", "timeout", "not_found", "partial"]
    payload: dict[str, Any] = Field(default_factory=dict)
    ambiguous: bool = False


class OracleEvent(FrozenRecord):
    sequence: int = Field(ge=1)
    event: Literal[
        "mutation_attempted",
        "fault_activated",
        "mutation_committed",
        "mutation_rejected",
        "partial_commit",
        "wrong_target_commit",
        "duplicate_commit",
        "read_observed",
        "status_observed",
        "audit_observed",
        "visibility_advanced",
    ]
    operation_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class TraceStep(FrozenRecord):
    index: int = Field(ge=1)
    tool: str
    arguments: dict[str, Any]
    result: ToolResult


class ExecutionTrace(FrozenRecord):
    scenario_id: str
    plan_id: str
    fault_activated: bool
    failure_type: str | None
    derived_seed: int
    steps: list[TraceStep]
