from proofpath.planning.power import simulate_factorial_power, simulate_instruction_power


def test_power_simulation_is_deterministic_and_budget_monotone() -> None:
    config = {
        "simulation": {
            "seed": 7,
            "replicates": 200,
            "scenario_count": 24,
            "model_count": 2,
            "presentation_count": 2,
            "repetition_grid": [1, 2],
            "baseline_logit_intercept": 0.0,
            "instruction_log_odds_effect": 0.4054651081081642,
            "scenario_random_intercept_sd": 0.5,
            "model_random_intercept_sd": 0.25,
            "alpha": 0.05,
            "confirmatory_family_size": 2,
            "target_power": 0.8,
            "factorial_effects": {
                "intercept": 0.4,
                "premium_scaled": -0.4,
                "risk_scaled": 0.2,
                "severity_high": 0.2,
                "instruction_verify": 0.4,
                "premium_by_risk": 0.4,
                "premium_by_severity": 0.4,
            },
        },
        "interpretation": {
            "smallest_effect_size_of_interest": 0.1,
            "limitation": "test",
        },
    }
    first = simulate_instruction_power(config)
    second = simulate_instruction_power(config)
    assert first == second
    assert first["power_grid"][0]["total_registered_choice_calls"] == 192
    assert first["power_grid"][1]["total_registered_choice_calls"] == 384


def test_factorial_power_reports_all_target_terms() -> None:
    config = {
        "simulation": {
            "seed": 7,
            "replicates": 20,
            "scenario_count": 96,
            "model_count": 3,
            "presentation_count": 4,
            "repetition_grid": [1],
            "baseline_logit_intercept": 0.0,
            "instruction_log_odds_effect": 0.4,
            "scenario_random_intercept_sd": 0.5,
            "model_random_intercept_sd": 0.25,
            "alpha": 0.05,
            "confirmatory_family_size": 5,
            "target_power": 0.8,
            "factorial_effects": {
                "intercept": 0.4,
                "premium_scaled": -0.4,
                "risk_scaled": 0.2,
                "severity_high": 0.2,
                "instruction_verify": 0.4,
                "premium_by_risk": 0.4,
                "premium_by_severity": 0.4,
            },
        },
        "interpretation": {
            "smallest_effect_size_of_interest": 0.1,
            "limitation": "test",
        },
    }
    report = simulate_factorial_power(config)
    assert report["target_terms"] == [
        "premium_scaled",
        "premium_by_risk",
        "premium_by_severity",
    ]
