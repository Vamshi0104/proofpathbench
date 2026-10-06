from proofpath.planning.cost import estimate_cost


def test_cost_estimate_scales_by_model_rate() -> None:
    pricing = {
        "source": "test",
        "captured_at": "2026-01-01",
        "per_million_tokens": {
            "cheap": {"input": 1.0, "output": 2.0},
            "expensive": {"input": 10.0, "output": 20.0},
        },
        "estimation": {
            "characters_per_input_token": 4.0,
            "expected_output_tokens_per_call": 100,
            "upper_output_tokens_per_call": 300,
            "warning": "test",
        },
    }
    report = estimate_cost(pricing, ["cheap", "expensive"])
    cheap = report["per_model"]["cheap"]["estimated_standard_cost_usd"]
    expensive = report["per_model"]["expensive"]["estimated_standard_cost_usd"]
    assert expensive == 10 * cheap
