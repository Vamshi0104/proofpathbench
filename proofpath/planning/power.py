"""Simulation-based pilot budget check, run before empirical model responses."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import Any

import numpy as np
import yaml

from proofpath.benchmark.design import PILOT_PREMIUMS
from proofpath.benchmark.generate import generate_scenarios


def _expit(value: np.ndarray) -> np.ndarray:
    return np.asarray(1 / (1 + np.exp(-value)))


def simulate_instruction_power(config: dict[str, Any]) -> dict[str, Any]:
    settings = config["simulation"]
    simulations = int(settings["replicates"])
    scenarios = int(settings["scenario_count"])
    models = int(settings["model_count"])
    presentations = int(settings["presentation_count"])
    alpha = float(settings["alpha"])
    family_size = int(settings["confirmatory_family_size"])
    adjusted_alpha = alpha / family_size
    critical = NormalDist().inv_cdf(1 - adjusted_alpha)
    rng = np.random.default_rng(int(settings["seed"]))

    scenario_effects = rng.normal(
        0,
        float(settings["scenario_random_intercept_sd"]),
        size=(simulations, scenarios, 1),
    )
    model_effects = rng.normal(
        0,
        float(settings["model_random_intercept_sd"]),
        size=(simulations, 1, models),
    )
    baseline_linear = (
        float(settings["baseline_logit_intercept"]) + scenario_effects + model_effects
    )
    baseline_probability = _expit(baseline_linear)
    instructed_probability = _expit(
        baseline_linear + float(settings["instruction_log_odds_effect"])
    )
    marginal_effect = float(np.mean(instructed_probability - baseline_probability))
    clusters = scenarios * models

    grid: list[dict[str, Any]] = []
    for repetitions in settings["repetition_grid"]:
        calls_per_condition = presentations * int(repetitions)
        vanilla = rng.binomial(calls_per_condition, baseline_probability) / calls_per_condition
        instructed = (
            rng.binomial(calls_per_condition, instructed_probability) / calls_per_condition
        )
        differences = (instructed - vanilla).reshape(simulations, clusters)
        means = differences.mean(axis=1)
        standard_errors = differences.std(axis=1, ddof=1) / math.sqrt(clusters)
        z_scores = np.divide(
            means,
            standard_errors,
            out=np.zeros_like(means),
            where=standard_errors > 0,
        )
        estimated_power = float(np.mean(z_scores > critical))
        grid.append(
            {
                "repetitions_per_presentation": int(repetitions),
                "total_registered_choice_calls": (
                    scenarios * models * 2 * presentations * int(repetitions)
                ),
                "estimated_power": estimated_power,
                "monte_carlo_standard_error": math.sqrt(
                    estimated_power * (1 - estimated_power) / simulations
                ),
            }
        )

    target = float(settings["target_power"])
    qualifying = [
        item for item in grid if item["estimated_power"] >= target
    ]
    recommendation = min(
        qualifying,
        key=lambda item: item["repetitions_per_presentation"],
        default=None,
    )
    return {
        "scope": "prospective simulation; contains no observed model outcomes",
        "simulation_replicates": simulations,
        "seed": int(settings["seed"]),
        "adjusted_one_sided_alpha": adjusted_alpha,
        "critical_z": critical,
        "scenario_by_model_clusters": clusters,
        "assumed_marginal_instruction_effect": marginal_effect,
        "smallest_effect_size_of_interest": config["interpretation"][
            "smallest_effect_size_of_interest"
        ],
        "power_grid": grid,
        "minimum_repetition_recommendation": (
            recommendation["repetitions_per_presentation"] if recommendation else None
        ),
        "limitations": [
            config["interpretation"]["limitation"],
            "The result depends on the stated random-effect and Bernoulli assumptions.",
            "Provider failures, exclusions, model drift, and presentation-specific random effects are not simulated.",
        ],
    }


def _factorial_design(model_count: int) -> tuple[np.ndarray, list[str], np.ndarray]:
    scenarios = generate_scenarios()
    rows: list[list[float]] = []
    groups: list[int] = []
    names = [
        "intercept",
        "premium_scaled",
        "risk_scaled",
        "severity_high",
        "instruction_verify",
        "premium_by_risk",
        "premium_by_severity",
        "mechanism_status",
        "mechanism_multiple",
        *[f"domain_{index}" for index in range(1, 8)],
        *[f"model_{index}" for index in range(1, model_count)],
    ]
    domains = sorted({scenario.domain.value for scenario in scenarios})
    for scenario_index, scenario in enumerate(scenarios):
        risk = scenario.design_cell.disclosed_failure_probability / 0.2
        severity = float(scenario.design_cell.severity == "high")
        mechanism = scenario.plan(
            scenario.evidence_dominant_plan_id()
        ).evidence_mechanism
        for premium_value in PILOT_PREMIUMS:
            premium = premium_value - 1.0
            for model_index in range(model_count):
                for instruction in (0.0, 1.0):
                    rows.append(
                        [
                            1.0,
                            premium,
                            risk,
                            severity,
                            instruction,
                            premium * risk,
                            premium * severity,
                            float(mechanism == "transaction_status"),
                            float(mechanism == "multiple_source"),
                            *[
                                float(scenario.domain.value == domain)
                                for domain in domains[1:]
                            ],
                            *[
                                float(model_index == index)
                                for index in range(1, model_count)
                            ],
                        ]
                    )
                    groups.append(scenario_index)
    return np.asarray(rows, dtype=float), names, np.asarray(groups)


def simulate_factorial_power(config: dict[str, Any]) -> dict[str, Any]:
    """Approximate H3-H5 power using cluster-robust linear-probability fits."""
    settings = config["simulation"]
    simulations = int(settings["replicates"])
    models = int(settings["model_count"])
    presentations = int(settings["presentation_count"])
    alpha = float(settings["alpha"])
    family_size = int(settings["confirmatory_family_size"])
    critical = NormalDist().inv_cdf(1 - alpha / family_size)
    design, names, groups = _factorial_design(models)
    target_names = ["premium_scaled", "premium_by_risk", "premium_by_severity"]
    targets = [names.index(name) for name in target_names]
    effects = settings["factorial_effects"]
    true_beta = np.zeros(len(names))
    for name in (
        "intercept",
        "premium_scaled",
        "risk_scaled",
        "severity_high",
        "instruction_verify",
        "premium_by_risk",
        "premium_by_severity",
    ):
        true_beta[names.index(name)] = float(effects[name])

    base_linear = design @ true_beta
    scenario_count = int(settings["scenario_count"])
    model_count = int(settings["model_count"])
    rng = np.random.default_rng(int(settings["seed"]) + 1)
    scenario_effects = rng.normal(
        0,
        float(settings["scenario_random_intercept_sd"]),
        size=(simulations, scenario_count),
    )
    model_effects = rng.normal(
        0,
        float(settings["model_random_intercept_sd"]),
        size=(simulations, model_count),
    )
    row_models = np.tile(
        np.repeat(np.arange(model_count), 2),
        scenario_count * len(PILOT_PREMIUMS),
    )
    linear = (
        base_linear[None, :]
        + scenario_effects[:, groups]
        + model_effects[:, row_models]
    )
    probabilities = _expit(linear)
    bread = np.linalg.inv(design.T @ design)
    projection = bread @ design.T
    correction = (scenario_count / (scenario_count - 1)) * (
        (len(groups) - 1) / (len(groups) - len(names))
    )

    grid: list[dict[str, Any]] = []
    for repetitions in settings["repetition_grid"]:
        # Each premium receives one of the four rotated presentation variants.
        calls_per_row = int(repetitions)
        outcomes = rng.binomial(calls_per_row, probabilities) / calls_per_row
        estimates = outcomes @ projection.T
        residuals = outcomes - estimates @ design.T
        variances = np.zeros((simulations, len(targets)))
        target_bread = bread[:, targets]
        for group in range(scenario_count):
            indices = np.flatnonzero(groups == group)
            scores = residuals[:, indices] @ design[indices, :]
            projected_scores = scores @ target_bread
            variances += projected_scores * projected_scores
        standard_errors = np.sqrt(variances * correction)
        z_scores = estimates[:, targets] / standard_errors
        detected = np.column_stack(
            (
                z_scores[:, 0] < -critical,
                z_scores[:, 1] > critical,
                z_scores[:, 2] > critical,
            )
        )
        grid.append(
            {
                "repetitions_per_presentation": int(repetitions),
                "total_registered_choice_calls": (
                    scenario_count * models * 2 * presentations * int(repetitions)
                ),
                "estimated_power": {
                    name: float(np.mean(detected[:, index]))
                    for index, name in enumerate(target_names)
                },
            }
        )
    return {
        "scope": "prospective simulation; contains no observed model outcomes",
        "method": (
            "cluster-robust linear-probability approximation to the prospectively specified "
            "factorial logistic analysis"
        ),
        "critical_z": critical,
        "target_terms": target_names,
        "assumed_log_odds_coefficients": {
            name: float(true_beta[names.index(name)]) for name in target_names
        },
        "power_grid": grid,
        "limitation": config["interpretation"]["limitation"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    report = {
        "instruction_contrast": simulate_instruction_power(config),
        "factorial_effects": simulate_factorial_power(config),
    }
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
