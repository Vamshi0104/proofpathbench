"""Deterministic fault specifications used by the mock execution environment."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


FailureType = Literal[
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


class FaultSpec(BaseModel):
    """A fully resolved, reproducible fault decision for one run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    activated: bool
    failure_type: FailureType | None = None
    derived_seed: int = Field(ge=0)
    draw: float = Field(ge=0, lt=1)

    def model_post_init(self, __context: object) -> None:
        if self.activated != (self.failure_type is not None):
            raise ValueError("activated and failure_type must agree")
