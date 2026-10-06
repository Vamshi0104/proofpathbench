"""CLI for non-empirical smoke or empirical manipulation checks."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import cast

from proofpath.agents import FixtureAdapter, ModelAdapter, OpenAIResponsesAdapter
from proofpath.agents.openai_responses import ReasoningEffort
from proofpath.benchmark.generate import PROJECT_ROOT
from proofpath.benchmark.validate import load_scenarios
from proofpath.manipulation import run_manipulation_check
from proofpath.prepilot import prepilot_audit


MANIPULATION_PREREQUISITES = (
    "runtime_validation",
    "blinded_human_review",
    "instruction_power_and_budget",
    "interaction_power_review",
    "model_snapshots_frozen",
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "pilot.yaml")
    parser.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    parser.add_argument("--model")
    parser.add_argument(
        "--reasoning-effort",
        choices=("none", "low", "medium", "high", "xhigh", "max"),
        default="none",
    )
    parser.add_argument("--confirm-review-complete", action="store_true")
    args = parser.parse_args()
    adapter: ModelAdapter
    if args.provider == "openai":
        if not args.model:
            parser.error("--model is required with --provider openai")
        if not args.confirm_review_complete:
            parser.error("empirical manipulation checks require completed blinded review")
        audit = prepilot_audit(args.config.resolve())
        missing = [
            name
            for name in MANIPULATION_PREREQUISITES
            if not audit["checks"][name]["passed"]
        ]
        if missing:
            parser.error(
                "empirical manipulation prerequisites are incomplete: " + ", ".join(missing)
            )
        adapter = OpenAIResponsesAdapter(
            args.model,
            reasoning_effort=cast(ReasoningEffort, args.reasoning_effort),
        )
        design_empirical_eligible = True
    else:
        adapter = FixtureAdapter()
        design_empirical_eligible = False
    directory = run_manipulation_check(
        scenarios=load_scenarios(),
        adapter=adapter,
        run_id=args.run_id,
        output_root=PROJECT_ROOT / "results" / "raw",
        design_empirical_eligible=design_empirical_eligible,
    )
    print(directory)


if __name__ == "__main__":
    main()
