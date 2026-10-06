"""Generate and adjudicate blinded human-review materials for ProofPathBench."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from proofpath.benchmark.generate import PROJECT_ROOT
from proofpath.benchmark.render import TOOL_DESCRIPTIONS
from proofpath.benchmark.validate import load_scenarios


PACKET_DIR = PROJECT_ROOT / "research" / "reviewer_packets"
KEY_PATH = PROJECT_ROOT / "tmp" / "human_validation_private" / "review_key.json"
FORM_FIELDS = [
    "review_id",
    "semantic_equivalent",
    "stronger_evidence_candidate",
    "wording_bias_candidate",
    "notes",
]


def _review_id(scenario_id: str, seed: int) -> str:
    digest = hashlib.sha256(f"{seed}:{scenario_id}".encode()).hexdigest()[:12]
    return f"review-{digest}"


def generate_review_packet(seed: int = 20260928) -> tuple[Path, Path]:
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = load_scenarios()
    rng = random.Random(seed)
    rng.shuffle(scenarios)
    packet_path = PACKET_DIR / "review_items.jsonl"
    form_path = PACKET_DIR / "review_form_template.csv"
    key_entries: list[dict[str, Any]] = []

    with packet_path.open("w", encoding="utf-8") as packet, form_path.open(
        "w", encoding="utf-8", newline=""
    ) as form:
        writer = csv.DictWriter(form, fieldnames=FORM_FIELDS)
        writer.writeheader()
        for scenario in scenarios:
            review_id = _review_id(scenario.scenario_id, seed)
            plan_ids = ["A", "B"]
            rng.shuffle(plan_ids)
            public_labels = {plan_ids[0]: "X", plan_ids[1]: "Y"}
            plans = []
            for plan_id in plan_ids:
                plan = scenario.plan(plan_id)
                plans.append(
                    {
                        "candidate": public_labels[plan_id],
                        "steps": [
                            {
                                "tool_description": TOOL_DESCRIPTIONS[step.tool],
                                "arguments": step.arguments,
                                "simulated_cost_units": step.cost_units,
                                "simulated_latency_ms": step.latency_ms,
                            }
                            for step in plan.steps
                        ],
                        "total_simulated_cost_units": plan.total_cost_units,
                        "total_simulated_latency_ms": plan.total_latency_ms,
                    }
                )
            packet.write(
                json.dumps(
                    {
                        "review_id": review_id,
                        "task": scenario.goal,
                        "required_outcome": scenario.postcondition.model_dump(mode="json"),
                        "collateral_constraints": [
                            item.model_dump(mode="json")
                            for item in scenario.collateral_constraints
                        ],
                        "candidates": plans,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            writer.writerow(
                {
                    "review_id": review_id,
                    "semantic_equivalent": "",
                    "stronger_evidence_candidate": "",
                    "wording_bias_candidate": "",
                    "notes": "",
                }
            )
            dominant = scenario.evidence_dominant_plan_id()
            key_entries.append(
                {
                    "review_id": review_id,
                    "scenario_id": scenario.scenario_id,
                    "candidate_to_plan_id": {
                        public_labels["A"]: "A",
                        public_labels["B"]: "B",
                    },
                    "expected_stronger_evidence_candidate": public_labels[dominant],
                }
            )
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    KEY_PATH.write_text(
        json.dumps(
            {
                "warning": "Evaluator-only mapping. Do not distribute with blinded packet.",
                "seed": seed,
                "items": key_entries,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return packet_path, form_path


def _read_reviews(path: Path) -> dict[str, dict[str, str]]:
    allowed_semantic = {"yes", "no", "uncertain"}
    allowed_evidence = {"X", "Y", "equal", "incomparable", "uncertain"}
    allowed_bias = {"none", "X", "Y", "uncertain"}
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    reviews: dict[str, dict[str, str]] = {}
    for row in rows:
        review_id = row.get("review_id", "")
        if not review_id or review_id in reviews:
            raise ValueError(f"missing or duplicate review_id in {path}")
        if row.get("semantic_equivalent") not in allowed_semantic:
            raise ValueError(f"{review_id}: invalid semantic_equivalent in {path}")
        if row.get("stronger_evidence_candidate") not in allowed_evidence:
            raise ValueError(f"{review_id}: invalid stronger_evidence_candidate in {path}")
        if row.get("wording_bias_candidate") not in allowed_bias:
            raise ValueError(f"{review_id}: invalid wording_bias_candidate in {path}")
        reviews[review_id] = row
    return reviews


def _cohen_kappa(left: list[str], right: list[str]) -> float | None:
    if len(left) != len(right) or not left:
        return None
    observed = sum(a == b for a, b in zip(left, right, strict=True)) / len(left)
    left_counts = Counter(left)
    right_counts = Counter(right)
    expected = sum(
        left_counts[label] * right_counts[label] for label in set(left_counts) | set(right_counts)
    ) / (len(left) ** 2)
    if expected == 1:
        return 1.0 if observed == 1 else None
    return (observed - expected) / (1 - expected)


def adjudicate_reviews(first_path: Path, second_path: Path) -> dict[str, Any]:
    key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    expected = {item["review_id"]: item for item in key["items"]}
    first = _read_reviews(first_path)
    second = _read_reviews(second_path)
    if set(first) != set(expected) or set(second) != set(expected):
        raise ValueError("each reviewer file must contain every review item exactly once")

    ordered_ids = sorted(expected)
    semantic_left = [first[item]["semantic_equivalent"] for item in ordered_ids]
    semantic_right = [second[item]["semantic_equivalent"] for item in ordered_ids]
    evidence_left = [first[item]["stronger_evidence_candidate"] for item in ordered_ids]
    evidence_right = [second[item]["stronger_evidence_candidate"] for item in ordered_ids]
    agreements = [
        item
        for item in ordered_ids
        if first[item]["semantic_equivalent"] == "yes"
        and second[item]["semantic_equivalent"] == "yes"
        and first[item]["stronger_evidence_candidate"]
        == expected[item]["expected_stronger_evidence_candidate"]
        and second[item]["stronger_evidence_candidate"]
        == expected[item]["expected_stronger_evidence_candidate"]
        and first[item]["wording_bias_candidate"] == "none"
        and second[item]["wording_bias_candidate"] == "none"
    ]
    disagreements = [item for item in ordered_ids if item not in agreements]
    return {
        "complete": True,
        "item_count": len(ordered_ids),
        "unanimous_accept_count": len(agreements),
        "requires_adjudication_count": len(disagreements),
        "requires_adjudication_review_ids": disagreements,
        "semantic_raw_agreement": sum(
            a == b for a, b in zip(semantic_left, semantic_right, strict=True)
        )
        / len(ordered_ids),
        "semantic_cohen_kappa": _cohen_kappa(semantic_left, semantic_right),
        "evidence_raw_agreement": sum(
            a == b for a, b in zip(evidence_left, evidence_right, strict=True)
        )
        / len(ordered_ids),
        "evidence_cohen_kappa": _cohen_kappa(evidence_left, evidence_right),
        "admission_ready_without_adjudication": not disagreements,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate")
    generate.add_argument("--seed", type=int, default=20260928)
    adjudicate = subparsers.add_parser("adjudicate")
    adjudicate.add_argument("--reviewer-1", type=Path, required=True)
    adjudicate.add_argument("--reviewer-2", type=Path, required=True)
    adjudicate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "generate":
        packet_path, form_path = generate_review_packet(args.seed)
        print(packet_path)
        print(form_path)
        return

    report = adjudicate_reviews(args.reviewer_1, args.reviewer_2)
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
