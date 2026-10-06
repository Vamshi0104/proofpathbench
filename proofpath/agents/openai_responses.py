"""OpenAI Responses API adapter with strict structured output."""

from __future__ import annotations

import time
from typing import Any, Literal

from proofpath.agents.models import ModelResponse

ReasoningEffort = Literal["none", "low", "medium", "high", "xhigh", "max"]


class OpenAIResponsesAdapter:
    provider = "openai"
    empirical_eligible = True

    def __init__(
        self,
        model: str,
        *,
        max_output_tokens: int = 300,
        temperature: float | None = None,
        reasoning_effort: ReasoningEffort = "none",
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError(
                "OpenAI adapter requires the optional openai package; install project dependencies"
            ) from error
        self.model = model
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self._client = OpenAI()

    def complete(self, prompt: str, response_schema: dict[str, Any]) -> ModelResponse:
        request: dict[str, Any] = {
            "model": self.model,
            "input": [{"role": "user", "content": prompt}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "proofpath_plan_choice",
                    "strict": True,
                    "schema": response_schema,
                }
            },
            "max_output_tokens": self.max_output_tokens,
            "reasoning": {"effort": self.reasoning_effort},
            "store": False,
        }
        if self.temperature is not None:
            request["temperature"] = self.temperature

        started = time.perf_counter()
        response = self._client.responses.create(**request)
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        usage = response.usage.model_dump(mode="json") if response.usage else {}
        return ModelResponse(
            provider=self.provider,
            requested_model=self.model,
            resolved_model=response.model,
            response_id=response.id,
            output_text=response.output_text,
            usage=usage,
            metadata={
                "status": response.status,
                "service_tier": getattr(response, "service_tier", None),
                "store": False,
                "reasoning_effort": self.reasoning_effort,
            },
            elapsed_ms=elapsed_ms,
            empirical_eligible=True,
        )
