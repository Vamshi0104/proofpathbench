import random

import pandas as pd
import pytest

from proofpath.evaluation import statistics
from proofpath.evaluation.statistics import _baseline_rate_test, holm_adjust


def test_holm_adjustment_is_monotone_and_bounded() -> None:
    adjusted = holm_adjust({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adjusted["a"] == 0.03
    assert adjusted["c"] == 0.06
    assert adjusted["b"] == 0.06
    assert all(0 <= value <= 1 for value in adjusted.values())


def test_h1_uses_only_vanilla_zero_premium_records() -> None:
    frame = pd.DataFrame(
        [
            {
                "selected": selected,
                "scenario_id": f"s{scenario}",
                "resolved_model": f"m{model}",
                "instruction_verify": instruction,
                "premium_scaled": premium,
            }
            for scenario, model, selected, instruction, premium in [
                (1, 1, 1, 0, 0.0),
                (2, 1, 1, 0, 0.0),
                (3, 1, 0, 0, 0.0),
                (4, 1, 1, 0, 0.0),
                (1, 2, 0, 0, 0.0),
                (2, 2, 1, 0, 0.0),
                (3, 2, 1, 0, 0.0),
                (4, 2, 1, 0, 0.0),
                (1, 1, 0, 1, 0.0),
                (1, 1, 0, 0, 0.5),
            ]
        ]
    )
    result = _baseline_rate_test(frame)
    assert result["record_count"] == 8
    assert result["estimate"] == pytest.approx(0.75)
    assert result["null_value"] == 0.5
    assert result["direction"] == "positive"
    assert 0 <= result["one_sided_p_unadjusted"] <= 1


def test_primary_report_separates_confirmatory_and_estimation_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = []
    rng = random.Random(7)
    mechanisms = ["independent_readback", "transaction_status", "multiple_source"]
    domains = [
        "filesystem",
        "database",
        "calendar",
        "messaging",
        "commerce",
        "profile",
    ]
    scenario_factors = {
        scenario: (
            rng.choice((0.0, 0.25, 1.0)),
            rng.choice((0, 1)),
            rng.choice(mechanisms),
            rng.choice(domains),
        )
        for scenario in range(96)
    }
    for scenario in range(96):
        risk, severity, mechanism, domain = scenario_factors[scenario]
        for model in range(3):
            for premium_index, premium in enumerate((0.0, 0.1, 0.5, 1.0)):
                for instruction in (0, 1):
                    probability = 0.48 + 0.1 * instruction - 0.08 * premium + 0.03 * risk
                    rows.append(
                        {
                            "selected": int(rng.random() < probability),
                            "scenario_id": f"s{scenario}",
                            "resolved_model": f"m{model}",
                            "premium_scaled": premium,
                            "risk_scaled": risk,
                            "severity_high": severity,
                            "instruction_verify": instruction,
                            "strong_evidence_mechanism": mechanism,
                            "domain": domain,
                            "prompt_template": rng.choice(("p0", "p1")),
                            "displayed_dominant_first": rng.choice((0, 1)),
                        }
                    )
    frame = pd.DataFrame(rows)
    monkeypatch.setattr(statistics, "records_dataframe", lambda _: frame)

    report = statistics.fit_primary_model([])
    assert report["confirmatory_family"]["size"] == 2
    assert set(report["confirmatory_family"]["tests"]) == {"h1", "h2"}
    assert set(report["estimation_targets"]) == {
        "h3_design_average_premium_slope",
        "h4_premium_by_risk",
        "h5_premium_by_severity",
    }
    assert all("holm_adjusted_p" not in target for target in report["estimation_targets"].values())
