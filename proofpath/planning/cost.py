"""Prospective API-cost estimate from rendered pilot prompts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import yaml

from proofpath.benchmark.design import split_plot_presentations
from proofpath.benchmark.render import InstructionCondition, render_prompt
from proofpath.benchmark.validate import load_scenarios


def estimate_cost(pricing: dict[str, Any], models: list[str]) -> dict[str, Any]:
    units = split_plot_presentations(load_scenarios())
    conditions: tuple[InstructionCondition, ...] = ("vanilla", "verify_instruction")
    prompts = [
        render_prompt(scenario, variant, condition)
        for scenario, variant in units
        for condition in conditions
    ]
    characters_per_token = float(pricing["estimation"]["characters_per_input_token"])
    estimated_input_tokens = sum(
        math.ceil(len(prompt) / characters_per_token) for prompt in prompts
    )
    call_count = len(prompts)
    expected_output = call_count * int(
        pricing["estimation"]["expected_output_tokens_per_call"]
    )
    upper_output = call_count * int(
        pricing["estimation"]["upper_output_tokens_per_call"]
    )
    estimates: dict[str, Any] = {}
    for model in models:
        rates = pricing["per_million_tokens"][model]
        input_cost = estimated_input_tokens / 1_000_000 * float(rates["input"])
        expected_cost = input_cost + expected_output / 1_000_000 * float(rates["output"])
        upper_cost = input_cost + upper_output / 1_000_000 * float(rates["output"])
        estimates[model] = {
            "call_count": call_count,
            "estimated_input_tokens": estimated_input_tokens,
            "expected_output_tokens": expected_output,
            "upper_output_tokens": upper_output,
            "estimated_standard_cost_usd": expected_cost,
            "upper_output_allowance_cost_usd": upper_cost,
        }
    return {
        "scope": "prospective estimate; not a bill or observed token usage",
        "pricing_source": pricing["source"],
        "pricing_captured_at": str(pricing["captured_at"]),
        "assumptions": pricing["estimation"],
        "per_model": estimates,
        "combined_expected_standard_cost_usd": sum(
            item["estimated_standard_cost_usd"] for item in estimates.values()
        ),
        "combined_upper_output_allowance_cost_usd": sum(
            item["upper_output_allowance_cost_usd"] for item in estimates.values()
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pricing", type=Path, required=True)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    pricing = yaml.safe_load(args.pricing.read_text(encoding="utf-8"))
    report = estimate_cost(pricing, args.models)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
