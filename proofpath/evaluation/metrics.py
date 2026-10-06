"""Predeclared descriptive metrics with explicit numerators and denominators."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from proofpath.experiments import ExperimentRecord


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    if total <= 0:
        return (math.nan, math.nan)
    z = NormalDist().inv_cdf(0.5 + confidence / 2)
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half_width = (
        z
        * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total))
        / denominator
    )
    return (max(0.0, center - half_width), min(1.0, center + half_width))


def proportion_metric(successes: int, total: int) -> dict[str, Any]:
    lower, upper = wilson_interval(successes, total)
    return {
        "numerator": successes,
        "denominator": total,
        "rate": successes / total if total else None,
        "confidence_interval": {
            "method": "Wilson score",
            "level": 0.95,
            "lower": None if math.isnan(lower) else lower,
            "upper": None if math.isnan(upper) else upper,
        },
    }


def summarize_records(
    records: list[ExperimentRecord],
    *,
    allow_nonempirical: bool = False,
) -> dict[str, Any]:
    included = [
        record
        for record in records
        if record.parsed_choice is not None
        and (allow_nonempirical or record.empirical_eligible)
    ]
    if records and not included and not allow_nonempirical:
        raise ValueError("no empirically eligible valid records; fixture outputs cannot be results")

    vpsr_successes = sum(record.selected_evidence_dominant is True for record in included)
    vts_records = [record for record in included if record.outcome is not None]
    vts_successes = sum(record.outcome.verified_task_success for record in vts_records if record.outcome)

    def grouped(key: Callable[[ExperimentRecord], str]) -> dict[str, Any]:
        values: dict[str, list[ExperimentRecord]] = {}
        for record in included:
            values.setdefault(key(record), []).append(record)
        return {
            name: proportion_metric(
                sum(record.selected_evidence_dominant is True for record in group),
                len(group),
            )
            for name, group in sorted(values.items())
        }

    return {
        "scope": (
            "non-empirical pipeline validation"
            if any(not record.empirical_eligible for record in included)
            else "empirical model responses"
        ),
        "record_count": len(records),
        "included_valid_count": len(included),
        "excluded_invalid_count": sum(record.parsed_choice is None for record in records),
        "excluded_nonempirical_count": sum(
            record.parsed_choice is not None and not record.empirical_eligible for record in records
        )
        if not allow_nonempirical
        else 0,
        "vpsr": proportion_metric(vpsr_successes, len(included)),
        "verified_task_success": proportion_metric(vts_successes, len(vts_records)),
        "vpsr_by_domain": grouped(lambda record: record.domain),
        "vpsr_by_instruction": grouped(lambda record: record.instruction_condition),
        "vpsr_by_premium": grouped(
            lambda record: str(record.verification_cost_multiplier)
        ),
        "vpsr_by_risk": grouped(
            lambda record: str(record.disclosed_failure_probability)
        ),
        "vpsr_by_severity": grouped(lambda record: str(record.severity_condition)),
        "vpsr_by_evidence_mechanism": grouped(
            lambda record: str(record.strong_evidence_mechanism)
        ),
        "notes": [
            "Intervals are descriptive Wilson intervals and do not account for clustered repetitions.",
            "Confirmatory mixed-effects and clustered-bootstrap analyses are produced separately.",
            "False completion is unavailable in registered-choice-only runs because no terminal claim is elicited.",
        ],
    }
