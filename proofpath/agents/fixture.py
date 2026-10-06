"""Deterministic non-empirical adapter for pipeline validation only."""

from __future__ import annotations

import json
import time
from typing import Any, Literal

from proofpath.agents.models import ModelResponse


class FixtureAdapter:
    provider = "fixture"
    empirical_eligible = False

    def __init__(self, strategy: Literal["first", "A", "B"] = "first") -> None:
        self.strategy = strategy
        self.model = f"fixture-{strategy}"
        self._counter = 0

    def complete(self, prompt: str, response_schema: dict[str, Any]) -> ModelResponse:
        started = time.perf_counter()
        payload = json.loads(prompt)
        if "stronger_evidence_candidate" in response_schema.get("properties", {}):
            plans = payload["candidate_plans"]
            stronger = max(plans, key=lambda plan: len(plan["steps"]))["plan_id"]
            costs = {plan["plan_id"]: plan["total_simulated_cost_units"] for plan in plans}
            if costs["A"] == costs["B"]:
                costlier = "equal"
            else:
                costlier = max(costs, key=costs.get)  # type: ignore[arg-type]
            response_payload = {
                "stronger_evidence_candidate": stronger,
                "higher_total_cost_candidate": costlier,
                "rationale": "Deterministic fixture classification for pipeline validation.",
            }
        else:
            if self.strategy == "first":
                plan_id = payload["candidate_plans"][0]["plan_id"]
            else:
                plan_id = self.strategy
            response_payload = {
                "plan_id": plan_id,
                "rationale": "Deterministic fixture response for pipeline validation.",
            }
        self._counter += 1
        output = json.dumps(response_payload, sort_keys=True)
        return ModelResponse(
            provider=self.provider,
            requested_model=self.model,
            resolved_model=self.model,
            response_id=f"fixture-{self._counter:06d}",
            output_text=output,
            metadata={"strategy": self.strategy, "non_empirical": True},
            elapsed_ms=round((time.perf_counter() - started) * 1000),
            empirical_eligible=False,
        )
