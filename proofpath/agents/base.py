"""Minimal adapter protocol for registered-choice model calls."""

from __future__ import annotations

from typing import Any, Protocol

from proofpath.agents.models import ModelResponse


class ModelAdapter(Protocol):
    provider: str
    model: str
    empirical_eligible: bool

    def complete(self, prompt: str, response_schema: dict[str, Any]) -> ModelResponse: ...
