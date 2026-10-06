#!/usr/bin/env python3
"""Generate the blinded construct-review packet and analyze two completed reviews."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

from proofpath.benchmark.render import TOOL_DESCRIPTIONS
from proofpath.benchmark.validate import load_scenarios

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_SEED = 20261006
DEFAULT_PRIVATE_MANIFEST = ROOT / "tmp" / "human_validation_private" / "blinding_manifest.json"
SAMPLE_SIZE = 32
DOMAINS = (
    "filesystem", "database", "profile", "calendar", "messaging", "configuration",
    "commerce", "subscription",
)
NOMINAL_FIELDS = {
    "semantic_goal_equivalence": {"yes", "no", "uncertain"},
    "authorization_input_equivalence": {"yes", "no", "uncertain"},
    "no_fault_outcome_equivalence": {"yes", "no", "uncertain"},
    "evidence_dominant_candidate": {"X", "Y", "equal", "incomparable", "uncertain"},
    "presentation_bias": {"none", "X", "Y", "both", "uncertain"},
    "intended_answer_guess": {"X", "Y", "cannot_tell"},
    "severity_plausibility": {"plausible", "implausible", "uncertain"},
}
ORDINAL_FIELDS = {
    f"{dimension}_{candidate}": ("none", "weak", "strong", "uncertain")
    for dimension in ("independence", "authority", "specificity", "freshness", "linkage", "coverage")
    for candidate in ("x", "y")
}
ORDINAL_FIELDS["guess_confidence"] = ("low", "medium", "high", "uncertain")
FIELDS = ["review_id", "reviewer_id", *NOMINAL_FIELDS, *ORDINAL_FIELDS, "concerns"]


def _review_id(scenario_id: str, seed: int) -> str:
    return "hv-" + hashlib.sha256(f"{seed}:{scenario_id}".encode()).hexdigest()[:12]


def _pick_sample(seed: int) -> list[Any]:
    """Pick four per domain while favoring under-represented design levels."""
    rng = random.Random(seed)
    selected: list[Any] = []
    counts: Counter[tuple[str, Any]] = Counter()
    for domain in DOMAINS:
        pool = [scenario for scenario in load_scenarios() if scenario.domain.value == domain]
        rng.shuffle(pool)
        for _ in range(4):
            def score(scenario: Any) -> tuple[int, float]:
                dominant = scenario.plan(scenario.evidence_dominant_plan_id())
                values = (
                    ("premium", scenario.design_cell.verification_cost_multiplier),
                    ("risk", scenario.design_cell.disclosed_failure_probability),
                    ("severity", scenario.design_cell.severity),
                    ("mechanism", dominant.evidence_mechanism),
                    ("canonical_dominant", scenario.evidence_dominant_plan_id()),
                )
                return (sum(counts[value] for value in values), rng.random())

            chosen = min(pool, key=score)
            pool.remove(chosen)
            selected.append(chosen)
            dominant = chosen.plan(chosen.evidence_dominant_plan_id())
            for value in (
                ("premium", chosen.design_cell.verification_cost_multiplier),
                ("risk", chosen.design_cell.disclosed_failure_probability),
                ("severity", chosen.design_cell.severity),
                ("mechanism", dominant.evidence_mechanism),
                ("canonical_dominant", chosen.evidence_dominant_plan_id()),
            ):
                counts[value] += 1
    rng.shuffle(selected)
    return selected


def generate(seed: int = DEFAULT_SEED, private_manifest: Path = DEFAULT_PRIVATE_MANIFEST) -> None:
    scenarios = _pick_sample(seed)
    public_items: list[dict[str, Any]] = []
    private_items: list[dict[str, Any]] = []
    form_rows: list[dict[str, str]] = []
    for index, scenario in enumerate(scenarios):
        variant = scenario.presentation_variants[index % 4]
        dominant_id = scenario.evidence_dominant_plan_id()
        other_id = next(plan.plan_id for plan in scenario.candidate_plans if plan.plan_id != dominant_id)
        dominant_label = "X" if index % 2 == 0 else "Y"
        candidate_for = {
            dominant_id: dominant_label,
            other_id: "Y" if dominant_label == "X" else "X",
        }
        # Candidate display position is balanced separately from the hidden dominant label.
        labels_in_order = ("X", "Y") if (index // 2) % 2 == 0 else ("Y", "X")
        canonical_order = [
            next(plan_id for plan_id, label in candidate_for.items() if label == wanted)
            for wanted in labels_in_order
        ]
        candidates = []
        for plan_id in canonical_order:
            plan = scenario.plan(plan_id)
            candidates.append({
                "candidate": candidate_for[plan_id],
                "steps": [{
                    "tool": getattr(variant.tool_aliases, step.tool),
                    "tool_description": TOOL_DESCRIPTIONS[step.tool],
                    "arguments": step.arguments,
                    "simulated_cost_units": step.cost_units,
                    "simulated_latency_ms": step.latency_ms,
                } for step in plan.steps],
                "total_simulated_cost_units": plan.total_cost_units,
                "total_simulated_latency_ms": plan.total_latency_ms,
            })
        review_id = _review_id(scenario.scenario_id, seed)
        public_items.append({
            "review_id": review_id,
            "domain": scenario.domain.value,
            "task": scenario.goal,
            "required_outcome": scenario.postcondition.model_dump(mode="json"),
            "collateral_constraints": [item.model_dump(mode="json") for item in scenario.collateral_constraints],
            "fault_context": {"disclosed_mutation_fault_probability": scenario.failure_policy.disclosed_probability},
            "consequence_mechanics": scenario.severity.state_consequence,
            "candidates": candidates,
        })
        expected = candidate_for[scenario.evidence_dominant_plan_id()]
        private_items.append({
            "review_id": review_id,
            "scenario_id": scenario.scenario_id,
            "presentation_variant": variant.variant_id,
            "candidate_to_plan_id": {candidate_for[key]: key for key in candidate_for},
            "expected_evidence_dominant_candidate": expected,
            "verification_premium": scenario.design_cell.verification_cost_multiplier,
            "risk": scenario.design_cell.disclosed_failure_probability,
            "severity": scenario.design_cell.severity,
            "evidence_mechanism": scenario.plan(scenario.evidence_dominant_plan_id()).evidence_mechanism,
        })
        form_rows.append({field: review_id if field == "review_id" else "" for field in FIELDS})

    (HERE / "sampled_items.json").write_text(json.dumps({
        "notice": "Blinded review materials; expected labels and internal scenario identifiers are omitted.",
        "seed_commitment_sha256": hashlib.sha256(str(seed).encode()).hexdigest(),
        "sample_size": len(public_items),
        "items": public_items,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    private_manifest.parent.mkdir(parents=True, exist_ok=True)
    private_manifest.write_text(json.dumps({
        "warning": "PRIVATE ANSWER KEY. Do not give this file to reviewers or distribute in the public ancillary archive.",
        "seed": seed,
        "items": private_items,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (HERE / "review_form.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(form_rows)


def _read(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or set(rows[0]) != set(FIELDS):
        raise ValueError(f"{path}: columns do not match the released form")
    parsed: dict[str, dict[str, str]] = {}
    for row in rows:
        rid = row["review_id"].strip()
        if not rid or rid in parsed:
            raise ValueError(f"{path}: blank or duplicate review_id")
        if not row["reviewer_id"].strip():
            raise ValueError(f"{rid}: reviewer_id is required")
        for field, allowed in NOMINAL_FIELDS.items():
            if row[field].strip() not in allowed:
                raise ValueError(f"{rid}: invalid or missing {field}")
        for field, allowed in ORDINAL_FIELDS.items():
            if row[field].strip() not in allowed:
                raise ValueError(f"{rid}: invalid or missing {field}")
        parsed[rid] = {key: value.strip() for key, value in row.items()}
    return parsed


def _kappa(left: list[str], right: list[str], order: tuple[str, ...] | None = None) -> float | None:
    if len(left) != len(right) or not left:
        return None
    labels = list(order or sorted(set(left) | set(right)))
    n = len(left)
    li, ri = Counter(left), Counter(right)
    if order is None:
        observed_disagreement = sum(a != b for a, b in zip(left, right, strict=True)) / n
        expected_disagreement = 1 - sum(li[x] * ri[x] for x in labels) / (n * n)
    else:
        span = max(1, len(labels) - 1)
        rank = {value: index for index, value in enumerate(labels)}
        def weight(a: str, b: str) -> float:
            return ((rank[a] - rank[b]) / span) ** 2

        observed_disagreement = sum(weight(a, b) for a, b in zip(left, right, strict=True)) / n
        expected_disagreement = sum(li[a] * ri[b] * weight(a, b) for a in labels for b in labels) / (n * n)
    if expected_disagreement == 0:
        return 1.0 if observed_disagreement == 0 else None
    return 1 - observed_disagreement / expected_disagreement


def analyze(first_path: Path, second_path: Path, manifest_path: Path | None) -> dict[str, Any]:
    first, second = _read(first_path), _read(second_path)
    public = json.loads((HERE / "sampled_items.json").read_text(encoding="utf-8"))
    expected_ids = {item["review_id"] for item in public["items"]}
    if set(first) != expected_ids or set(second) != expected_ids:
        raise ValueError("each reviewer file must contain every released review_id exactly once")
    ordered = sorted(expected_ids)
    agreement: dict[str, Any] = {}
    def contingency(left: list[str], right: list[str]) -> dict[str, int]:
        return dict(sorted(Counter(f"{a}|{b}" for a, b in zip(left, right, strict=True)).items()))

    for field in NOMINAL_FIELDS:
        left, right = [first[x][field] for x in ordered], [second[x][field] for x in ordered]
        agreement[field] = {
            "raw": sum(a == b for a, b in zip(left, right, strict=True)) / len(ordered),
            "cohen_kappa": _kappa(left, right),
            "reviewer_pair_counts": contingency(left, right),
        }
    for field, levels in ORDINAL_FIELDS.items():
        left, right = [first[x][field] for x in ordered], [second[x][field] for x in ordered]
        valid_pairs = [(a, b) for a, b in zip(left, right, strict=True) if "uncertain" not in {a, b}]
        weighted_left = [a for a, _ in valid_pairs]
        weighted_right = [b for _, b in valid_pairs]
        agreement[field] = {
            "raw": sum(a == b for a, b in zip(left, right, strict=True)) / len(ordered),
            "quadratic_weighted_kappa": _kappa(weighted_left, weighted_right, levels[:-1]),
            "weighted_kappa_non_uncertain_pair_count": len(valid_pairs),
            "reviewer_pair_counts": contingency(left, right),
        }
    disagreements = [rid for rid in ordered if any(first[rid][field] != second[rid][field] for field in (*NOMINAL_FIELDS, *ORDINAL_FIELDS))]
    report: dict[str, Any] = {
        "status": "complete_two_reviewer_analysis",
        "item_count": len(ordered),
        "agreement": agreement,
        "requires_adjudication_review_ids": disagreements,
        "acceptance_thresholds": {"semantic_raw_agreement": 0.80, "evidence_raw_agreement": 0.80, "nominal_kappa": 0.60, "ordinal_weighted_kappa": 0.60},
        "automatic_admission_decision": False,
        "note": "Thresholds diagnose reliability; disagreements still require documented human adjudication before empirical use.",
    }
    if manifest_path:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        truth = {item["review_id"]: item["expected_evidence_dominant_candidate"] for item in manifest["items"]}
        if set(truth) != expected_ids:
            raise ValueError("private manifest does not match released sample")
        report["expected_dominance_match"] = {
            name: sum(reviews[rid]["evidence_dominant_candidate"] == truth[rid] for rid in ordered) / len(ordered)
            for name, reviews in (("reviewer_1", first), ("reviewer_2", second))
        }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate")
    gen.add_argument("--seed", type=int, default=DEFAULT_SEED)
    gen.add_argument("--private-manifest", type=Path, default=DEFAULT_PRIVATE_MANIFEST)
    ana = sub.add_parser("analyze")
    ana.add_argument("--reviewer-1", type=Path, required=True)
    ana.add_argument("--reviewer-2", type=Path, required=True)
    ana.add_argument("--manifest", type=Path)
    ana.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate(args.seed, args.private_manifest)
        print(f"generated {SAMPLE_SIZE} blinded review items in {HERE}")
        print(f"private manifest: {args.private_manifest}")
        return
    report = analyze(args.reviewer_1, args.reviewer_2, args.manifest)
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
