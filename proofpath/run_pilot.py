"""Run a ProofPathBench registered-choice smoke check or preregistered pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

import yaml

from proofpath.agents import FixtureAdapter, ModelAdapter, OpenAIResponsesAdapter
from proofpath.agents.openai_responses import ReasoningEffort
from proofpath.benchmark.design import split_plot_presentations, validate_split_plot
from proofpath.benchmark.generate import PROJECT_ROOT
from proofpath.benchmark.render import InstructionCondition
from proofpath.benchmark.validate import load_scenarios
from proofpath.evaluation.metrics import summarize_records
from proofpath.experiments import load_records, run_registered_choice
from proofpath.prepilot import prepilot_audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=("smoke", "registered-choice"),
        default="smoke",
    )
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "pilot.yaml")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--provider", choices=("fixture", "openai"), default="fixture")
    parser.add_argument("--model")
    parser.add_argument(
        "--reasoning-effort",
        choices=("none", "low", "medium", "high", "xhigh", "max"),
        default="none",
    )
    parser.add_argument("--fixture-strategy", choices=("first", "A", "B"), default="first")
    parser.add_argument("--max-scenarios", type=int)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument(
        "--confirm-preregistered",
        action="store_true",
        help="assert that external human-review and preregistration requirements are complete",
    )
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    scenarios = load_scenarios()

    adapter: ModelAdapter
    conditions: tuple[InstructionCondition, ...]
    variants: tuple[str, ...]
    if args.stage == "smoke":
        if args.provider != "fixture":
            parser.error("smoke stage intentionally uses the fixture provider")
        adapter = FixtureAdapter(args.fixture_strategy)
        scenario_limit = args.max_scenarios or 4
        scenarios = scenarios[:scenario_limit]
        conditions = ("vanilla", "verify_instruction")
        variants = ("p1-o1", "p1-o2")
        repetitions = args.repetitions or 1
        design_empirical_eligible = False
    else:
        if args.provider == "fixture":
            parser.error("fixture outputs cannot be used for the registered-choice pilot")
        if not args.model:
            parser.error("--model is required for an empirical provider")
        if not args.confirm_preregistered:
            parser.error(
                "registered-choice requires --confirm-preregistered after the human-review "
                "and design-freeze checklist is complete"
            )
        if config["study"].get("status") != "preregistered":
            parser.error("config study.status must be preregistered before empirical runs")
        audit = prepilot_audit(config_path)
        if not audit["eligible_for_empirical_pilot"]:
            parser.error(
                "pre-pilot audit is incomplete: " + ", ".join(audit["next_actions"])
            )
        if args.max_scenarios:
            parser.error("empirical registered-choice runs cannot use --max-scenarios")
        adapter = OpenAIResponsesAdapter(
            args.model,
            reasoning_effort=cast(ReasoningEffort, args.reasoning_effort),
        )
        conditions = ("vanilla", "verify_instruction")
        variants = ("p1-o1", "p1-o2", "p2-o1", "p2-o2")
        repetitions = args.repetitions or config["study"]["repetitions_per_presentation"]
        design_empirical_eligible = True

    presentation_units = None
    if args.stage == "registered-choice":
        presentation_units = split_plot_presentations(scenarios)
        split_errors = validate_split_plot(presentation_units)
        if split_errors:
            parser.error(f"split-plot design invalid: {split_errors}")

    run_directory = run_registered_choice(
        scenarios=scenarios,
        adapter=adapter,
        run_id=args.run_id,
        output_root=PROJECT_ROOT / "results" / "raw",
        config_path=config_path,
        master_seed=config["study"]["master_seed"],
        instruction_conditions=conditions,
        variants=variants,
        repetitions=repetitions,
        design_empirical_eligible=design_empirical_eligible,
        presentation_units=presentation_units,
    )
    records = load_records(run_directory / "records.jsonl")
    summary = summarize_records(records, allow_nonempirical=args.stage == "smoke")
    (run_directory / "descriptive_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(run_directory)


if __name__ == "__main__":
    main()
