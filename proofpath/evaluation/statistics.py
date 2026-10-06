"""Prospective confirmatory analysis for empirical pilot records."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import statsmodels.api as sm  # type: ignore[import-untyped]
import statsmodels.formula.api as smf  # type: ignore[import-untyped]
from scipy.stats import norm  # type: ignore[import-untyped]
from statsmodels.stats.sandwich_covariance import (  # type: ignore[import-untyped]
    cov_cluster,
    cov_cluster_2groups,
)

from proofpath.experiments import ExperimentRecord

PRIMARY_FORMULA = (
    "selected ~ premium_scaled + risk_scaled + severity_high + instruction_verify + "
    "premium_scaled:risk_scaled + premium_scaled:severity_high + "
    "C(strong_evidence_mechanism) + C(domain) + C(prompt_template) + "
    "displayed_dominant_first + C(resolved_model)"
)


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    count = len(ordered)
    for rank, (name, value) in enumerate(ordered):
        candidate = min(1.0, (count - rank) * value)
        running = max(running, candidate)
        adjusted[name] = running
    return adjusted


def records_dataframe(records: list[ExperimentRecord]) -> pd.DataFrame:
    eligible = [
        record
        for record in records
        if record.empirical_eligible and record.parsed_choice is not None
    ]
    if not eligible:
        raise ValueError("confirmatory analysis requires empirically eligible valid records")
    if len(eligible) != len(records):
        raise ValueError("resolve and report exclusions before confirmatory analysis")
    rows = []
    for record in eligible:
        if (
            record.verification_cost_multiplier is None
            or record.disclosed_failure_probability is None
            or record.severity_condition is None
            or record.strong_evidence_mechanism is None
            or record.prompt_template is None
            or record.displayed_plan_order is None
        ):
            raise ValueError(f"{record.run_key}: missing preregistered factor fields")
        rows.append(
            {
                "selected": int(record.selected_evidence_dominant is True),
                "scenario_id": record.scenario_id,
                "resolved_model": record.model_response.resolved_model,
                "premium_scaled": record.verification_cost_multiplier - 1.0,
                "risk_scaled": record.disclosed_failure_probability / 0.2,
                "severity_high": int(record.severity_condition == "high"),
                "instruction_verify": int(record.instruction_condition == "verify_instruction"),
                "strong_evidence_mechanism": record.strong_evidence_mechanism,
                "domain": record.domain,
                "prompt_template": record.prompt_template,
                "displayed_dominant_first": int(
                    record.displayed_plan_order[0] == record.evidence_dominant_plan_id
                ),
            }
        )
    return pd.DataFrame(rows)


def _cluster_covariance(fit: Any, frame: pd.DataFrame) -> tuple[np.ndarray, str]:
    scenario_groups = pd.factorize(frame["scenario_id"], sort=True)[0]
    model_count = int(frame["resolved_model"].nunique())
    # A model-cluster sandwich with only a handful of model families is unstable and can
    # produce invalid covariance estimates. The reference pilot has three models, which
    # are included as fixed effects in the primary GLM; scenario clustering is the
    # defensible finite-sample covariance. Two-way clustering is reserved for a later
    # study with enough distinct model clusters for the sandwich approximation.
    if model_count >= 20:
        model_groups = pd.factorize(frame["resolved_model"], sort=True)[0]
        covariance, _, _ = cov_cluster_2groups(
            fit,
            scenario_groups,
            model_groups,
        )
        return np.asarray(covariance), "two-way scenario/model cluster robust"
    return (
        np.asarray(cov_cluster(fit, scenario_groups)),
        (
            f"scenario cluster robust; {model_count} model clusters are too few for "
            "model-cluster sandwich inference"
        ),
    )


def _one_sided_p_value(z_value: float, direction: str) -> float:
    if direction == "positive":
        return float(norm.sf(z_value))
    if direction == "negative":
        return float(norm.cdf(z_value))
    raise ValueError(f"unsupported direction: {direction}")


def _baseline_rate_test(frame: pd.DataFrame) -> dict[str, Any]:
    """Test H1 as a marginal clustered rate contrast against chance.

    An intercept-only linear-probability model makes the estimand exactly the observed
    vanilla, zero-premium VPSR. Cluster-robust uncertainty preserves the scenario/model
    dependence structure without making the GLM intercept depend on arbitrary nuisance
    reference levels.
    """
    baseline = frame[(frame["instruction_verify"] == 0) & (frame["premium_scaled"] == 0)].copy()
    if baseline.empty:
        raise ValueError("H1 requires vanilla records at zero verification premium")
    fit = smf.ols("selected ~ 1", data=baseline).fit()
    covariance, covariance_method = _cluster_covariance(fit, baseline)
    rate = float(fit.params.iloc[0])
    standard_error = float(np.sqrt(covariance[0, 0]))
    difference = rate - 0.5
    if standard_error == 0:
        z_value = math.copysign(math.inf, difference) if difference else 0.0
    else:
        z_value = difference / standard_error
    return {
        "hypothesis": "vanilla zero-premium VPSR exceeds 0.5",
        "direction": "positive",
        "estimate": rate,
        "null_value": 0.5,
        "difference_from_null": difference,
        "cluster_robust_standard_error": standard_error,
        "confidence_interval_95": [
            max(0.0, rate - 1.96 * standard_error),
            min(1.0, rate + 1.96 * standard_error),
        ],
        "z": z_value,
        "one_sided_p_unadjusted": _one_sided_p_value(z_value, "positive"),
        "record_count": len(baseline),
        "scenario_count": int(baseline["scenario_id"].nunique()),
        "model_count": int(baseline["resolved_model"].nunique()),
        "covariance": covariance_method,
    }


def _linear_combination(
    fit: Any,
    covariance: np.ndarray,
    weights: dict[str, float],
) -> tuple[float, float]:
    names = list(fit.params.index)
    vector = np.zeros(len(names))
    for name, weight in weights.items():
        vector[names.index(name)] = weight
    estimate = float(vector @ np.asarray(fit.params))
    standard_error = float(np.sqrt(vector @ covariance @ vector))
    return estimate, standard_error


def _log_odds_result(
    estimate: float,
    standard_error: float,
    *,
    direction: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "log_odds_estimate": estimate,
        "odds_ratio": math.exp(estimate),
        "cluster_robust_standard_error": standard_error,
        "confidence_interval_95_log_odds": [
            estimate - 1.96 * standard_error,
            estimate + 1.96 * standard_error,
        ],
    }
    if direction is not None:
        z_value = estimate / standard_error if standard_error else math.copysign(math.inf, estimate)
        result.update(
            {
                "direction": direction,
                "z": z_value,
                "one_sided_p_unadjusted": _one_sided_p_value(z_value, direction),
            }
        )
    return result


def fit_primary_model(records: list[ExperimentRecord]) -> dict[str, Any]:
    frame = records_dataframe(records)
    fit = smf.glm(PRIMARY_FORMULA, data=frame, family=sm.families.Binomial()).fit()
    covariance, covariance_method = _cluster_covariance(fit, frame)
    names = list(fit.params.index)
    standard_errors = np.sqrt(np.diag(covariance))

    h1 = _baseline_rate_test(frame)
    instruction_index = names.index("instruction_verify")
    h2 = {
        "hypothesis": "verify instruction increases VPSR",
        **_log_odds_result(
            float(fit.params.iloc[instruction_index]),
            float(standard_errors[instruction_index]),
            direction="positive",
        ),
    }
    confirmatory_tests = {"h1": h1, "h2": h2}
    adjusted = holm_adjust(
        {
            name: float(result["one_sided_p_unadjusted"])
            for name, result in confirmatory_tests.items()
        }
    )
    for name, value in adjusted.items():
        confirmatory_tests[name]["holm_adjusted_p"] = value

    # H3 is the design-average premium slope on the log-odds scale. It is intentionally
    # estimation-only in the pilot because prospective power is inadequate. Averaging
    # the interaction weights avoids interpreting only the zero-risk/low-severity cell.
    premium_estimate, premium_se = _linear_combination(
        fit,
        covariance,
        {
            "premium_scaled": 1.0,
            "premium_scaled:risk_scaled": float(frame["risk_scaled"].mean()),
            "premium_scaled:severity_high": float(frame["severity_high"].mean()),
        },
    )
    estimation_targets = {
        "h3_design_average_premium_slope": {
            "hypothesis": "VPSR decreases as the verification premium increases",
            "direction": "negative",
            "status": "estimation_only_in_pilot",
            **_log_odds_result(premium_estimate, premium_se),
        },
        "h4_premium_by_risk": {
            "hypothesis": "higher disclosed risk attenuates the negative premium slope",
            "direction": "positive",
            "status": "estimation_only_in_pilot",
            **_log_odds_result(
                float(fit.params["premium_scaled:risk_scaled"]),
                float(standard_errors[names.index("premium_scaled:risk_scaled")]),
            ),
        },
        "h5_premium_by_severity": {
            "hypothesis": "high severity attenuates the negative premium slope",
            "direction": "positive",
            "status": "estimation_only_in_pilot",
            **_log_odds_result(
                float(fit.params["premium_scaled:severity_high"]),
                float(standard_errors[names.index("premium_scaled:severity_high")]),
            ),
        },
    }
    return {
        "formula": PRIMARY_FORMULA,
        "record_count": len(frame),
        "scenario_count": int(frame["scenario_id"].nunique()),
        "model_count": int(frame["resolved_model"].nunique()),
        "covariance": covariance_method,
        "converged": bool(fit.converged),
        "confirmatory_family": {
            "method": "Holm",
            "size": 2,
            "tests": confirmatory_tests,
        },
        "estimation_targets": estimation_targets,
        "all_coefficients": {
            name: {
                "estimate": float(fit.params.iloc[index]),
                "standard_error": float(standard_errors[index]),
            }
            for index, name in enumerate(names)
        },
        "warning": (
            "H3-H5 are pilot estimation targets. Do not interpret their intervals or signs as "
            "confirmatory findings; use blinded pilot variance estimates to size a later study."
        ),
    }
