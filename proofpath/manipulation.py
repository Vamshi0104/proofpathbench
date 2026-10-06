"""Manipulation-check runner and preregistered pass-rule computation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from proofpath.agents import ManipulationChoice, ModelAdapter, ModelResponse
from proofpath.benchmark.models import Scenario
from proofpath.benchmark.render import render_manipulation_prompt
from proofpath.evaluation.metrics import proportion_metric


class ManipulationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_schema_version: Literal["0.1"] = "0.1"
    run_id: str
    scenario_id: str
    domain: str
    presentation_variant: str
    prompt_sha256: str
    prompt: str
    model_response: ModelResponse
    parsed_choice: ManipulationChoice | None
    parse_error: str | None
    expected_stronger_evidence_candidate: str
    expected_higher_total_cost_candidate: str
    evidence_classification_correct: bool | None
    cost_classification_correct: bool | None
    empirical_eligible: bool


def _parse(response: ModelResponse) -> tuple[ManipulationChoice | None, str | None]:
    try:
        return ManipulationChoice.model_validate_json(response.output_text), None
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"


def run_manipulation_check(
    *,
    scenarios: list[Scenario],
    adapter: ModelAdapter,
    run_id: str,
    output_root: Path,
    variant_id: str = "p1-o1",
    design_empirical_eligible: bool = True,
) -> Path:
    run_directory = output_root / run_id
    if run_directory.exists():
        raise FileExistsError(f"refusing to overwrite existing run directory: {run_directory}")
    run_directory.mkdir(parents=True)
    schema = ManipulationChoice.model_json_schema()
    records_path = run_directory / "records.jsonl"
    with records_path.open("x", encoding="utf-8") as stream:
        for scenario in scenarios:
            prompt = render_manipulation_prompt(scenario, variant_id)
            response = adapter.complete(prompt, schema)
            choice, parse_error = _parse(response)
            dominant_id = scenario.evidence_dominant_plan_id()
            expected_cost = (
                "equal"
                if scenario.design_cell.verification_cost_multiplier == 1.0
                else dominant_id
            )
            record = ManipulationRecord(
                run_id=run_id,
                scenario_id=scenario.scenario_id,
                domain=scenario.domain.value,
                presentation_variant=variant_id,
                prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                prompt=prompt,
                model_response=response,
                parsed_choice=choice,
                parse_error=parse_error,
                expected_stronger_evidence_candidate=dominant_id,
                expected_higher_total_cost_candidate=expected_cost,
                evidence_classification_correct=(
                    choice.stronger_evidence_candidate == dominant_id if choice else None
                ),
                cost_classification_correct=(
                    choice.higher_total_cost_candidate == expected_cost if choice else None
                ),
                empirical_eligible=(
                    response.empirical_eligible and design_empirical_eligible
                ),
            )
            stream.write(record.model_dump_json() + "\n")

    manifest = {
        "run_id": run_id,
        "stage": "manipulation-check",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "provider": adapter.provider,
        "requested_model": adapter.model,
        "scenario_count": len(scenarios),
        "presentation_variant": variant_id,
        "empirical_eligible": adapter.empirical_eligible and design_empirical_eligible,
    }
    (run_directory / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    records = load_manipulation_records(records_path)
    summary = summarize_manipulation(records, allow_nonempirical=not manifest["empirical_eligible"])
    (run_directory / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return run_directory


def load_manipulation_records(path: Path) -> list[ManipulationRecord]:
    return [
        ManipulationRecord.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize_manipulation(
    records: list[ManipulationRecord],
    *,
    allow_nonempirical: bool = False,
) -> dict[str, object]:
    included = [
        record
        for record in records
        if record.parsed_choice is not None
        and (record.empirical_eligible or allow_nonempirical)
    ]
    if records and not included:
        raise ValueError("no eligible manipulation-check records")
    overall = proportion_metric(
        sum(record.evidence_classification_correct is True for record in included),
        len(included),
    )
    by_domain: dict[str, object] = {}
    for domain in sorted({record.domain for record in included}):
        group = [record for record in included if record.domain == domain]
        by_domain[domain] = proportion_metric(
            sum(record.evidence_classification_correct is True for record in group),
            len(group),
        )
    overall_lower = overall["confidence_interval"]["lower"]
    domain_lowers = [
        metric["confidence_interval"]["lower"]  # type: ignore[index]
        for metric in by_domain.values()
    ]
    empirical = all(record.empirical_eligible for record in included)
    thresholds_met = bool(
        overall_lower is not None
        and overall_lower >= 0.85
        and domain_lowers
        and min(domain_lowers) >= 0.75
    )
    return {
        "scope": "empirical model responses" if empirical else "non-empirical pipeline validation",
        "included_count": len(included),
        "invalid_count": sum(record.parsed_choice is None for record in records),
        "evidence_classification": overall,
        "evidence_classification_by_domain": by_domain,
        "cost_classification": proportion_metric(
            sum(record.cost_classification_correct is True for record in included),
            len(included),
        ),
        "preregistered_thresholds": {
            "overall_lower_95_bound_minimum": 0.85,
            "per_domain_lower_95_bound_minimum": 0.75,
        },
        "thresholds_numerically_met": thresholds_met,
        "pass_for_pilot": thresholds_met and empirical,
        "note": "Non-empirical fixture output can test arithmetic but can never pass the pilot gate.",
    }
